"""Rich terminal display for acquisition brief components."""
from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from models import AcquisitionBrief, IPPortfolio, LitigationProfile, RegulatoryExposure, ContractProfile
from config import TIER_COLORS

console = Console()


def _color(tier: str) -> str:
    return TIER_COLORS.get(tier, "white")


def print_ip_portfolio(ip: IPPortfolio) -> None:
    color = _color(ip.strength_tier)
    console.print(f"\n[bold]IP Portfolio — {ip.company}[/bold]")
    console.print(f"Strength tier: [{color}]{ip.strength_tier}[/{color}]  |  "
                  f"Total patents: {ip.total_patents}  |  "
                  f"Avg citations: {ip.avg_citations:.1f}")

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    tbl.add_column("Metric", style="dim", width=30)
    tbl.add_column("Value")

    vel_arrow = "+" if ip.velocity_change_pct >= 0 else "-"
    vel_color = "green" if ip.velocity_change_pct >= 0 else "yellow"
    tbl.add_row("Recent velocity (3yr avg)", f"{ip.patent_velocity:.1f} patents/yr")
    tbl.add_row("Baseline velocity", f"{ip.baseline_velocity:.1f} patents/yr")
    tbl.add_row(
        "Velocity change",
        f"[{vel_color}]{vel_arrow} {ip.velocity_change_pct:+.1f}%[/{vel_color}]",
    )
    tbl.add_row("Recent patents (3yr)", str(ip.recent_patents))
    tbl.add_row("Top technology domains", ", ".join(ip.top_domains[:3]) or "—")
    console.print(tbl)

    if ip.patents:
        ptbl = Table(box=box.SIMPLE, show_header=True, header_style="bold", title="Sample Patents")
        ptbl.add_column("Patent ID", style="dim", width=16)
        ptbl.add_column("Title", width=50)
        ptbl.add_column("Filed", width=12)
        ptbl.add_column("Cites", justify="right")
        for p in ip.patents[:8]:
            ptbl.add_row(p.patent_id, p.title[:50], p.filing_date[:7], str(p.forward_citations))
        console.print(ptbl)


def print_litigation(lit: LitigationProfile) -> None:
    color = _color(lit.risk_tier)
    console.print(f"\n[bold]Litigation Profile — {lit.company}[/bold]")
    console.print(
        f"Risk tier: [{color}]{lit.risk_tier}[/{color}]  |  "
        f"Active: {lit.active_cases}  |  IP disputes: {lit.ip_disputes}  |  "
        f"Regulatory: {lit.regulatory_actions}  |  Settled (3yr): {lit.settled_last_3yr}"
    )

    if not lit.cases:
        console.print("[dim]  No cases found.[/dim]")
        return

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    tbl.add_column("Case", width=42)
    tbl.add_column("Court", width=30)
    tbl.add_column("Filed", width=12)
    tbl.add_column("Status", width=10)
    tbl.add_column("Type", width=14)
    for c in lit.cases:
        status_color = "red" if c.status == "ACTIVE" else "green" if c.status == "SETTLED" else "dim"
        tbl.add_row(
            c.case_name[:42], c.court[:30], c.filed_date[:10],
            f"[{status_color}]{c.status}[/{status_color}]", c.case_type,
        )
    console.print(tbl)


def print_regulatory(reg: RegulatoryExposure) -> None:
    color = _color(reg.exposure_tier)
    mw_color  = "red"   if reg.material_weakness else "green"
    gc_color  = "red"   if reg.going_concern     else "green"
    console.print(f"\n[bold]Regulatory Exposure — {reg.company} ({reg.ticker})[/bold]")
    console.print(
        f"Exposure tier: [{color}]{reg.exposure_tier}[/{color}]  |  "
        f"Material weakness: [{mw_color}]{reg.material_weakness}[/{mw_color}]  |  "
        f"Going concern: [{gc_color}]{reg.going_concern}[/{gc_color}]  |  "
        f"Export control mentions: {reg.export_control_mentions}  |  "
        f"Gov revenue: {reg.government_revenue_pct*100:.0f}%"
    )

    if reg.flags:
        tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        tbl.add_column("Flag", width=22)
        tbl.add_column("Severity", width=14)
        tbl.add_column("Period", width=8)
        tbl.add_column("Description", width=55)
        for f in reg.flags:
            sev_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(f.severity, "dim")
            tbl.add_row(
                f.flag_type, f"[{sev_color}]{f.severity}[/{sev_color}]",
                f.filing_period, f.description[:55],
            )
        console.print(tbl)


def print_contracts(cont: ContractProfile) -> None:
    color = _color(cont.dependency_tier)
    console.print(f"\n[bold]Contract Profile — {cont.company}[/bold]")
    console.print(
        f"Dependency tier: [{color}]{cont.dependency_tier}[/{color}]  |  "
        f"Total awards: {cont.total_awards}  |  "
        f"Total value: ${cont.total_value_usd:,.0f}  |  "
        f"Primary: {cont.primary_agency} ({cont.primary_agency_pct*100:.0f}%)  |  "
        f"Recent (2yr): {cont.recent_awards}"
    )

    if cont.agency_breakdown:
        tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold", title="Agency Breakdown")
        tbl.add_column("Agency", width=35)
        tbl.add_column("Total ($)", justify="right", width=18)
        tbl.add_column("Share", justify="right", width=8)
        tbl.add_column("Bar", width=20)
        total = cont.total_value_usd or 1
        for agency, val in sorted(cont.agency_breakdown.items(), key=lambda x: -x[1]):
            pct = val / total
            bar = "#" * max(1, int(pct * 20)) + "." * (20 - max(1, int(pct * 20)))
            tbl.add_row(agency[:35], f"${val:,.0f}", f"{pct*100:.0f}%", bar)
        console.print(tbl)


def print_brief(brief: AcquisitionBrief) -> None:
    risk_color = _color(brief.overall_risk_tier)
    header = (
        f"[bold]Pre-Acquisition Intelligence Brief[/bold]\n"
        f"Target: {brief.company} ({brief.ticker})  |  "
        f"Overall Risk: [{risk_color}]{brief.overall_risk_tier}[/{risk_color}]  |  "
        f"Prepared: {brief.prepared_date}"
    )
    console.print(Panel(header, border_style="cyan"))
    console.print(Panel(brief.full_text, border_style="dim", title="Full Brief", expand=True))


def print_brief_summary(brief: AcquisitionBrief) -> None:
    risk_color = _color(brief.overall_risk_tier)
    console.print(f"\n[bold]Pre-Acquisition Brief — {brief.company} ({brief.ticker})[/bold]")
    console.print(
        f"Overall risk: [{risk_color}]{brief.overall_risk_tier}[/{risk_color}]  |  "
        f"Prepared: {brief.prepared_date}"
    )

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold", title="Domain Summary")
    tbl.add_column("Domain", width=26)
    tbl.add_column("Tier", width=18)
    tbl.add_column("Key Metric", width=40)

    ip  = brief.ip_portfolio
    lit = brief.litigation_profile
    reg = brief.regulatory_exposure
    con = brief.contract_profile

    tbl.add_row(
        "IP Portfolio",
        f"[{_color(ip.strength_tier)}]{ip.strength_tier}[/{_color(ip.strength_tier)}]",
        f"{ip.total_patents} patents, {ip.patent_velocity:.1f}/yr, {ip.avg_citations:.1f} avg citations",
    )
    tbl.add_row(
        "Litigation",
        f"[{_color(lit.risk_tier)}]{lit.risk_tier}[/{_color(lit.risk_tier)}]",
        f"{lit.active_cases} active, {lit.ip_disputes} IP disputes, {lit.regulatory_actions} regulatory",
    )
    tbl.add_row(
        "Regulatory Exposure",
        f"[{_color(reg.exposure_tier)}]{reg.exposure_tier}[/{_color(reg.exposure_tier)}]",
        f"MW:{reg.material_weakness}  GC:{reg.going_concern}  EC mentions:{reg.export_control_mentions}",
    )
    tbl.add_row(
        "Contract Dependency",
        f"[{_color(con.dependency_tier)}]{con.dependency_tier}[/{_color(con.dependency_tier)}]",
        f"{con.primary_agency} {con.primary_agency_pct*100:.0f}%, ${con.total_value_usd/1e6:.0f}M total",
    )
    console.print(tbl)

    if brief.diligence_questions:
        console.print("\n[bold]Recommended Diligence Questions:[/bold]")
        for i, q in enumerate(brief.diligence_questions[:5], 1):
            console.print(f"  {i}. {q[:120]}")
