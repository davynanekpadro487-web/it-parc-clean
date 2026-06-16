from odoo import models, fields, api
import io
import base64

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

class ItExportExcel(models.Model):
    _name = 'it.equipement'
    _inherit = 'it.equipement'

    def action_export_inventaire_excel(self):
        if not xlsxwriter:
            raise Exception(
                'xlsxwriter non installé. '
                'Exécutez : pip install xlsxwriter'
            )
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Inventaire')

        # Formats
        titre = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_color': 'white',
            'bg_color': '#1a3c5e',
            'align': 'center', 'valign': 'vcenter',
            'border': 1
        })
        entete = workbook.add_format({
            'bold': True, 'font_color': 'white',
            'bg_color': '#1a3c5e',
            'border': 1, 'align': 'center'
        })
        cellule = workbook.add_format({
            'border': 1, 'align': 'left'
        })
        montant = workbook.add_format({
            'border': 1, 'num_format': '#,##0',
            'align': 'right'
        })
        rouge = workbook.add_format({
            'border': 1, 'font_color': 'red',
            'bold': True
        })
        orange = workbook.add_format({
            'border': 1, 'font_color': '#FF8C00',
            'bold': True
        })

        # Titre
        worksheet.merge_range(
            'A1:J1',
            'INVENTAIRE COMPLET DU PARC INFORMATIQUE - TECHPARK CI',
            titre
        )
        worksheet.set_row(0, 30)

        # En-têtes
        colonnes = [
            'Référence', 'Nom', 'Catégorie', 'Marque',
            'Modèle', 'N° Série', 'Employé', 'Département',
            'État', 'Fin Garantie', 'Jours Garantie',
            'Localisation', 'Date Achat', 'Valeur (FCFA)'
        ]
        largeurs = [
            15, 25, 15, 15, 15, 20, 20, 20,
            12, 15, 12, 15, 15, 15
        ]
        for col, (nom, larg) in enumerate(
            zip(colonnes, largeurs)
        ):
            worksheet.write(1, col, nom, entete)
            worksheet.set_column(col, col, larg)

        # Données
        categories = dict(
            self._fields['categorie'].selection
        )
        etats = dict(self._fields['state'].selection)
        
        equipements = self.search([])
        for row, eq in enumerate(equipements, start=2):
            worksheet.write(row, 0, eq.reference, cellule)
            worksheet.write(row, 1, eq.name, cellule)
            worksheet.write(
                row, 2,
                categories.get(eq.categorie, ''),
                cellule
            )
            worksheet.write(
                row, 3, eq.marque or '', cellule
            )
            worksheet.write(
                row, 4, eq.modele or '', cellule
            )
            worksheet.write(
                row, 5, eq.numero_serie or '', cellule
            )
            worksheet.write(
                row, 6,
                eq.employee_id.name if eq.employee_id
                else '', cellule
            )
            worksheet.write(
                row, 7,
                eq.department_id.name if eq.department_id
                else '', cellule
            )
            worksheet.write(
                row, 8,
                etats.get(eq.state, ''), cellule
            )
            worksheet.write(
                row, 9,
                str(eq.date_garantie) if eq.date_garantie
                else '', cellule
            )
            
            # Jours garantie avec couleur
            jours = eq.jours_garantie_restants
            fmt = rouge if jours < 0 else (
                orange if jours < 30 else cellule
            )
            worksheet.write(row, 10, jours, fmt)
            
            worksheet.write(
                row, 11, eq.localisation or '', cellule
            )
            worksheet.write(
                row, 12,
                str(eq.date_achat) if eq.date_achat
                else '', cellule
            )
            worksheet.write(
                row, 13, eq.valeur_achat, montant
            )

        workbook.close()
        output.seek(0)
        
        # Créer pièce jointe
        attachment = self.env['ir.attachment'].create({
            'name': 'inventaire_it_parc.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': (
                'application/vnd.openxmlformats-'
                'officedocument.spreadsheetml.sheet'
            ),
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}'
                   f'?download=true',
            'target': 'self',
        }

    def action_export_couts_maintenance_excel(self):
        if not xlsxwriter:
            raise Exception('xlsxwriter non installé.')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet(
            'Coûts Maintenance'
        )

        entete = workbook.add_format({
            'bold': True, 'font_color': 'white',
            'bg_color': '#1a3c5e',
            'border': 1, 'align': 'center'
        })
        cellule = workbook.add_format({
            'border': 1
        })
        montant = workbook.add_format({
            'border': 1, 'num_format': '#,##0',
            'align': 'right'
        })
        titre = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_color': 'white',
            'bg_color': '#1a3c5e',
            'align': 'center'
        })

        worksheet.merge_range(
            'A1:F1',
            'SYNTHÈSE DES COÛTS DE MAINTENANCE - TECHPARK CI',
            titre
        )
        worksheet.set_row(0, 30)

        colonnes = [
            'Équipement', 'Référence', 'Catégorie',
            'Nb Interventions', 'Durée Totale (h)',
            'Coût Total (FCFA)'
        ]
        largeurs = [25, 15, 15, 18, 18, 20]
        for col, (nom, larg) in enumerate(
            zip(colonnes, largeurs)
        ):
            worksheet.write(1, col, nom, entete)
            worksheet.set_column(col, col, larg)

        categories = dict(
            self._fields['categorie'].selection
        )
        equipements = self.search([])
        total_cout = 0
        
        for row, eq in enumerate(equipements, start=2):
            worksheet.write(row, 0, eq.name, cellule)
            worksheet.write(
                row, 1, eq.reference, cellule
            )
            worksheet.write(
                row, 2,
                categories.get(eq.categorie, ''),
                cellule
            )
            worksheet.write(
                row, 3, eq.nb_interventions, cellule
            )
            duree = sum(
                eq.intervention_ids.mapped('duree')
            )
            worksheet.write(row, 4, duree, cellule)
            worksheet.write(
                row, 5, eq.cout_total_maintenance, montant
            )
            total_cout += eq.cout_total_maintenance

        # Ligne total
        total_fmt = workbook.add_format({
            'bold': True, 'border': 1,
            'bg_color': '#D3D3D3',
            'num_format': '#,##0'
        })
        derniere_ligne = len(equipements) + 2
        worksheet.write(
            derniere_ligne, 4, 'TOTAL', total_fmt
        )
        worksheet.write(
            derniere_ligne, 5, total_cout, total_fmt
        )

        workbook.close()
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': 'couts_maintenance_it_parc.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': (
                'application/vnd.openxmlformats-'
                'officedocument.spreadsheetml.sheet'
            ),
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}'
                   f'?download=true',
            'target': 'self',
        }


class ItExportContrats(models.Model):
    _name = 'it.contrat'
    _inherit = 'it.contrat'

    def action_export_contrats_excel(self):
        if not xlsxwriter:
            raise Exception('xlsxwriter non installé.')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet(
            'Contrats Expirants'
        )

        titre = workbook.add_format({
            'bold': True, 'font_size': 14,
            'font_color': 'white',
            'bg_color': '#1a3c5e',
            'align': 'center'
        })
        entete = workbook.add_format({
            'bold': True, 'font_color': 'white',
            'bg_color': '#1a3c5e',
            'border': 1, 'align': 'center'
        })
        cellule = workbook.add_format({'border': 1})
        montant = workbook.add_format({
            'border': 1, 'num_format': '#,##0',
            'align': 'right'
        })
        rouge = workbook.add_format({
            'border': 1, 'bg_color': '#FFB3B3',
            'font_color': 'red', 'bold': True
        })
        orange = workbook.add_format({
            'border': 1, 'bg_color': '#FFE4B5',
            'font_color': '#FF8C00'
        })

        worksheet.merge_range(
            'A1:G1',
            'CONTRATS EXPIRANT DANS LES 60 JOURS - TECHPARK CI',
            titre
        )
        worksheet.set_row(0, 30)

        colonnes = [
            'Contrat', 'Fournisseur', 'Type',
            'Date Début', 'Date Fin',
            'Jours Restants', 'Montant (FCFA)'
        ]
        largeurs = [25, 25, 15, 15, 15, 15, 18]
        for col, (nom, larg) in enumerate(
            zip(colonnes, largeurs)
        ):
            worksheet.write(1, col, nom, entete)
            worksheet.set_column(col, col, larg)

        from datetime import date, timedelta
        limite = date.today() + timedelta(days=60)
        
        contrats = self.search([
            ('date_fin', '<=', str(limite)),
            ('state', '=', 'actif'),
        ], order='date_fin asc')
        
        types = dict(
            self._fields['type_contrat'].selection
        )
        
        for row, ct in enumerate(contrats, start=2):
            jours = ct.jours_restants
            fmt = rouge if jours < 30 else orange
            
            worksheet.write(row, 0, ct.name, fmt)
            worksheet.write(
                row, 1, ct.fournisseur_id.name, fmt
            )
            worksheet.write(
                row, 2,
                types.get(ct.type_contrat, ''), fmt
            )
            worksheet.write(
                row, 3, str(ct.date_debut), fmt
            )
            worksheet.write(
                row, 4, str(ct.date_fin), fmt
            )
            worksheet.write(row, 5, jours, fmt)
            worksheet.write(row, 6, ct.montant, montant)

        workbook.close()
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': 'contrats_expirants_it_parc.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': (
                'application/vnd.openxmlformats-'
                'officedocument.spreadsheetml.sheet'
            ),
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}'
                   f'?download=true',
            'target': 'self',
        }
