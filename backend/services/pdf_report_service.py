import os
from datetime import datetime
from typing import Optional
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from backend.config import settings

class PDFReportService:
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_consolidated_bi_report(
        self,
        session_id: int,
        kpi_data: dict,
        monthly_data: list,
        category_data: list,
        channel_data: list,
        store_data: list,
        stockout_data: list,
        strategy_text: str,
        verification_text: str,
        strategy_plan: Optional[dict] = None,
        scorecard: Optional[dict] = None
    ) -> str:
        filename = f"Business_Intelligence_Report_Session_{session_id}.pdf"
        file_path = os.path.join(self.reports_dir, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        )
        body_bold = ParagraphStyle(
            'BodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        callout_style = ParagraphStyle(
            'Callout',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#065F46')
        )

        elements = []

        # --- Header ---
        elements.append(Paragraph("APEX RETAIL ENTERPRISE | DECISION INTELLIGENCE", subtitle_style))
        elements.append(Paragraph("Executive Business Intelligence & Turnaround Report", title_style))
        elements.append(Paragraph(
            f"<b>Analysis Period:</b> May 1, 2026 – October 31, 2026 &nbsp;|&nbsp; "
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y')} &nbsp;|&nbsp; "
            f"<b>Session ID:</b> #{session_id} &nbsp;|&nbsp; "
            f"<b>Status:</b> <font color='#059669'>VERIFIED & CERTIFIED</font>",
            subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

        # --- Executive Summary ---
        elements.append(Paragraph("1. Executive Summary", section_style))
        summary_p = (
            f"During the six-month operating period from May 1 to October 31, 2026, the retail enterprise recorded "
            f"<b>₹{kpi_data['net_revenue']:,.2f}</b> in completed net revenue across <b>{kpi_data['completed_orders']:,}</b> orders, "
            f"generating a Gross Profit of <b>₹{kpi_data['gross_profit']:,.2f}</b> at a <b>{kpi_data['gross_profit_margin_pct']}%</b> gross margin. "
            f"However, cumulative store operating expenses totaled <b>₹{kpi_data['total_operating_expenses']:,.2f}</b>, "
            f"resulting in an operating {'profit' if kpi_data['net_operating_profit'] >= 0 else 'loss'} of "
            f"<b>₹{abs(kpi_data['net_operating_profit']):,.2f}</b> ({kpi_data['operating_margin_pct']}% operating margin). "
            f"{kpi_data['returned_orders']:,} orders were returned (₹{kpi_data['returned_revenue_lost']:,.2f} lost) and "
            f"{kpi_data['cancelled_orders']:,} were cancelled (₹{kpi_data['cancelled_revenue_lost']:,.2f} lost), a combined "
            f"<b>{kpi_data['order_return_rate_pct'] + kpi_data['order_cancellation_rate_pct']:.2f}%</b> of placed orders."
        )
        elements.append(Paragraph(summary_p, body_style))

        # --- Key Performance Indicators Table ---
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("2. Verified Core Retail Performance Metrics", section_style))

        kpi_table_data = [
            [
                Paragraph("<b>Metric</b>", body_bold),
                Paragraph("<b>Value</b>", body_bold),
                Paragraph("<b>Metric</b>", body_bold),
                Paragraph("<b>Value</b>", body_bold)
            ],
            [
                Paragraph("Total Transactions Placed", body_style),
                Paragraph(f"{kpi_data['total_transactions']:,}", body_style),
                Paragraph("Cost of Goods Sold (COGS)", body_style),
                Paragraph(f"₹{kpi_data['cogs']:,.2f}", body_style)
            ],
            [
                Paragraph("Completed Orders", body_style),
                Paragraph(f"{kpi_data['completed_orders']:,} ({kpi_data['order_completion_rate_pct']}%)", body_style),
                Paragraph("Gross Profit", body_style),
                Paragraph(f"₹{kpi_data['gross_profit']:,.2f}", body_style)
            ],
            [
                Paragraph("Total Net Revenue", body_style),
                Paragraph(f"₹{kpi_data['net_revenue']:,.2f}", body_style),
                Paragraph("Gross Profit Margin", body_style),
                Paragraph(f"{kpi_data['gross_profit_margin_pct']}%", body_style)
            ],
            [
                Paragraph("Average Order Value (AOV)", body_style),
                Paragraph(f"₹{kpi_data['aov']:,.2f}", body_style),
                Paragraph("Operating Expenses (OpEx)", body_style),
                Paragraph(f"₹{kpi_data['total_operating_expenses']:,.2f}", body_style)
            ],
            [
                Paragraph("Returned Orders (Leakage)", body_style),
                Paragraph(f"{kpi_data['returned_orders']:,} (₹{kpi_data['returned_revenue_lost']:,.2f})", body_style),
                Paragraph("Net Operating Profit (EBIT)", body_style),
                Paragraph(f"<font color='#DC2626'>-₹{abs(kpi_data['net_operating_profit']):,.2f}</font>", body_style)
            ],
            [
                Paragraph("Cancelled Orders", body_style),
                Paragraph(f"{kpi_data['cancelled_orders']:,} (₹{kpi_data['cancelled_revenue_lost']:,.2f})", body_style),
                Paragraph("Active / Repeat Customers", body_style),
                Paragraph(f"{kpi_data['active_customers']:,} / {kpi_data['repeat_customers']:,} ({kpi_data['repeat_purchase_rate_pct']}%)", body_style)
            ]
        ]

        kpi_table = Table(kpi_table_data, colWidths=[140, 130, 140, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(kpi_table)

        # --- Monthly Trajectory Table ---
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("3. Monthly Financial Trajectory (May – October 2026)", section_style))

        monthly_rows = [
            [
                Paragraph("<b>Month</b>", body_bold),
                Paragraph("<b>Completed Orders</b>", body_bold),
                Paragraph("<b>Net Revenue (₹)</b>", body_bold),
                Paragraph("<b>Gross Profit (₹)</b>", body_bold),
                Paragraph("<b>OpEx (₹)</b>", body_bold),
                Paragraph("<b>MoM Growth</b>", body_bold)
            ]
        ]
        for m in monthly_data:
            growth_str = f"{m['revenue_mom_growth_pct']}%" if m['revenue_mom_growth_pct'] != 0 else "-"
            growth_color = '#059669' if m['revenue_mom_growth_pct'] >= 0 else '#DC2626'
            monthly_rows.append([
                Paragraph(str(m['month']), body_style),
                Paragraph(f"{m['completed_orders']:,}", body_style),
                Paragraph(f"₹{m['net_revenue']:,.2f}", body_style),
                Paragraph(f"₹{m['gross_profit']:,.2f}", body_style),
                Paragraph(f"₹{m['operating_expenses']:,.2f}", body_style),
                Paragraph(f"<font color='{growth_color}'>{growth_str}</font>", body_style)
            ])

        m_table = Table(monthly_rows, colWidths=[70, 90, 110, 110, 100, 60])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(m_table)

        # --- Page Break ---
        elements.append(PageBreak())

        # --- Category & Channel Insights ---
        elements.append(Paragraph("4. Department & Channel Performance Breakdown", section_style))

        cat_rows = [
            [
                Paragraph("<b>Category</b>", body_bold),
                Paragraph("<b>Net Revenue (₹)</b>", body_bold),
                Paragraph("<b>Share</b>", body_bold),
                Paragraph("<b>Units Sold</b>", body_bold),
                Paragraph("<b>Gross Profit (₹)</b>", body_bold),
                Paragraph("<b>Margin %</b>", body_bold)
            ]
        ]
        for c in category_data:
            cat_rows.append([
                Paragraph(str(c['category']), body_style),
                Paragraph(f"₹{c['total_revenue']:,.2f}", body_style),
                Paragraph(f"{c['revenue_share_pct']}%", body_style),
                Paragraph(f"{c['total_units_sold']:,}", body_style),
                Paragraph(f"₹{c['gross_profit']:,.2f}", body_style),
                Paragraph(f"{c['gross_margin_pct']}%", body_style)
            ])

        cat_table = Table(cat_rows, colWidths=[100, 110, 60, 80, 110, 80])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(cat_table)

        # Channel table
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Channel Return Leakage Analysis", ParagraphStyle('Sub', parent=body_bold, fontSize=11, leading=14)))

        ch_rows = [
            [
                Paragraph("<b>Channel</b>", body_bold),
                Paragraph("<b>Total Orders</b>", body_bold),
                Paragraph("<b>Completed</b>", body_bold),
                Paragraph("<b>Returned</b>", body_bold),
                Paragraph("<b>Return Rate %</b>", body_bold),
                Paragraph("<b>Lost Sales (₹)</b>", body_bold)
            ]
        ]
        for ch in channel_data:
            ch_rows.append([
                Paragraph(str(ch['channel']), body_style),
                Paragraph(f"{ch['total_orders']:,}", body_style),
                Paragraph(f"{ch['completed_orders']:,}", body_style),
                Paragraph(f"{ch['returned_orders']:,}", body_style),
                Paragraph(f"{ch['return_rate_pct']}%", body_style),
                Paragraph(f"₹{ch['returned_lost_revenue']:,.2f}", body_style)
            ])

        ch_table = Table(ch_rows, colWidths=[90, 80, 80, 80, 90, 120])
        ch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(ch_table)

        # --- Stockout Hazards ---
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("5. Critical Warehouse Stockout Hazards", section_style))

        stock_rows = [
            [
                Paragraph("<b>SKU</b>", body_bold),
                Paragraph("<b>Product Name</b>", body_bold),
                Paragraph("<b>Category</b>", body_bold),
                Paragraph("<b>Current Stock</b>", body_bold),
                Paragraph("<b>Reorder Level</b>", body_bold),
                Paragraph("<b>Deficit</b>", body_bold)
            ]
        ]
        for s in stockout_data[:6]:
            stock_rows.append([
                Paragraph(str(s['product_id']), body_style),
                Paragraph(str(s['product_name'])[:28], body_style),
                Paragraph(str(s['category']), body_style),
                Paragraph(f"<font color='#DC2626'>{s['current_stock']} units</font>", body_style),
                Paragraph(f"{s['reorder_level']} units", body_style),
                Paragraph(f"{s['deficit']} units", body_bold)
            ])

        stk_table = Table(stock_rows, colWidths=[65, 175, 75, 75, 75, 75])
        stk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(stk_table)

        # --- Strategic Recommendations ---
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("6. Prioritized Strategic Turnaround Actions", section_style))
        plan = strategy_plan or {}
        for r in plan.get("recommendations", []):
            elements.append(Paragraph(
                f"• <b>({escape(str(r.get('category', '')))})</b> <b>{escape(str(r.get('title', '')))}</b>: "
                f"{escape(str(r.get('description', '')))} "
                f"<i>Expected impact: {escape(str(r.get('expected_roi', 'n/a')))}; "
                f"risk: {escape(str(r.get('risk_level', 'n/a')))}. Pending manager approval.</i>",
                body_style))
        if not plan.get("recommendations"):
            elements.append(Paragraph(escape(strategy_text or "No verified recommendations."), body_style))
        for title, key in (("Growth Opportunities", "growth_opportunities"),
                           ("Business Risks", "business_risks")):
            items = plan.get(key) or []
            if items:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph(f"<b>{title}</b>", body_bold))
                for it in items:
                    elements.append(Paragraph(f"• {escape(str(it))}", body_style))
        if plan.get("improvement_plan"):
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("<b>90-Day Improvement Plan</b>", body_bold))
            for ph in plan["improvement_plan"]:
                if isinstance(ph, dict):
                    acts = "; ".join(escape(str(x)) for x in ph.get("actions", []))
                    elements.append(Paragraph(
                        f"<b>{escape(str(ph.get('phase', '')))}</b> "
                        f"(owner: {escape(str(ph.get('owner', 'n/a')))}): {acts}", body_style))

        # --- Verification Sign-Off Box ---
        elements.append(Spacer(1, 12))
        sc = scorecard or {}
        approved = sc.get("final_verdict") == "APPROVED"
        colour = '#059669' if approved else '#DC2626'
        if sc:
            status_line = (
                f"<b>Verification Status:</b> <font color='{colour}'>{escape(str(sc.get('final_verdict')))}</font><br/>"
                f"Automated audit: {sc.get('verified_claims')} of {sc.get('claims_checked')} figures in the analyst "
                f"reports matched database values ({sc.get('mathematical_accuracy_pct')}% accuracy, threshold "
                f"{sc.get('accuracy_threshold_pct')}%). Unverified figures: {sc.get('hallucination_count')}. "
                f"Correction rounds: {sc.get('correction_rounds')}. Verification Agent verdict: "
                f"{escape(str(sc.get('agent_verdict')))} (confidence {escape(str(sc.get('agent_confidence')))}).<br/>"
                f"{escape(str(sc.get('agent_rationale', '')))}"
            )
        else:
            status_line = escape(verification_text or "No verification data available.")
        verif_box_data = [
            [Paragraph("<b>VERIFICATION AUDIT RESULT</b>", body_bold)],
            [Paragraph(status_line, callout_style)],
        ]
        verif_table = Table(verif_box_data, colWidths=[540])
        verif_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F0FDF4' if approved else '#FEF2F2')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(colour)),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(verif_table)

        doc.build(elements)
        return file_path
