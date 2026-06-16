from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import csv
import io

class WizardImportCsv(models.TransientModel):
    _name = 'wizard.import.csv'
    _description = 'Import CSV équipements'

    fichier_csv = fields.Binary(
        string='Fichier CSV', required=True
    )
    nom_fichier = fields.Char(string='Nom du fichier')
    delimiteur = fields.Selection([
        (',', 'Virgule (,)'),
        (';', 'Point-virgule (;)'),
    ], string='Délimiteur', default=';')
    
    nb_crees = fields.Integer(
        string='Créés', readonly=True
    )
    nb_ignores = fields.Integer(
        string='Ignorés (doublons)', readonly=True
    )
    nb_erreurs = fields.Integer(
        string='Erreurs', readonly=True
    )
    rapport = fields.Text(
        string='Rapport d\'import', readonly=True
    )
    state = fields.Selection([
        ('draft', 'Prêt'),
        ('done', 'Terminé'),
    ], default='draft')

    def action_importer(self):
        if not self.fichier_csv:
            raise UserError('Veuillez sélectionner un fichier CSV.')
        
        contenu = base64.b64decode(self.fichier_csv)
        fichier = io.StringIO(contenu.decode('utf-8-sig'))
        reader = csv.DictReader(
            fichier, delimiter=self.delimiteur
        )
        
        nb_crees = 0
        nb_ignores = 0
        nb_erreurs = 0
        rapport_lines = []
        
        colonnes_requises = ['name', 'categorie', 'numero_serie']
        categories_valides = [
            'poste_travail', 'serveur', 'imprimante',
            'reseau', 'telephone', 'autre'
        ]
        
        for i, ligne in enumerate(reader, start=2):
            try:
                # Vérifier colonnes requises
                for col in colonnes_requises:
                    if col not in ligne or not ligne[col]:
                        raise ValueError(
                            f'Colonne manquante : {col}'
                        )
                
                # Valider catégorie
                categorie = ligne.get('categorie', 'autre')
                if categorie not in categories_valides:
                    categorie = 'autre'
                
                # Vérifier doublon par numéro de série
                numero_serie = ligne.get('numero_serie', '')
                if numero_serie:
                    existing = self.env['it.equipement'].search([
                        ('numero_serie', '=', numero_serie)
                    ])
                    if existing:
                        nb_ignores += 1
                        rapport_lines.append(
                            f'Ligne {i}: IGNORÉ - '
                            f'Doublon série {numero_serie}'
                        )
                        continue
                
                # Créer l'équipement
                vals = {
                    'name': ligne['name'],
                    'categorie': categorie,
                    'numero_serie': numero_serie,
                    'marque': ligne.get('marque', ''),
                    'modele': ligne.get('modele', ''),
                    'localisation': ligne.get('localisation', ''),
                }
                
                if ligne.get('valeur_achat'):
                    try:
                        vals['valeur_achat'] = float(
                            ligne['valeur_achat']
                        )
                    except ValueError:
                        pass
                
                if ligne.get('date_garantie'):
                    vals['date_garantie'] = ligne['date_garantie']
                
                self.env['it.equipement'].create(vals)
                nb_crees += 1
                rapport_lines.append(
                    f'Ligne {i}: CRÉÉ - {ligne["name"]}'
                )
                
            except Exception as e:
                nb_erreurs += 1
                rapport_lines.append(
                    f'Ligne {i}: ERREUR - {str(e)}'
                )
        
        self.write({
            'nb_crees': nb_crees,
            'nb_ignores': nb_ignores,
            'nb_erreurs': nb_erreurs,
            'rapport': '\n'.join(rapport_lines),
            'state': 'done',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.import.csv',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
