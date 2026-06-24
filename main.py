"""CLI entry point — Pre-Acquisition Intelligence Brief Generator (P61)."""
from __future__ import annotations

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
from rich.console import Console

from config import DEMO_MODE, DEMO_COMPANY, DEMO_TICKER
from seed_data import DEMO_BRIEF

console = Console()


def _run_pipeline(company: str, ticker: str, demo: bool) -> "AcquisitionBrief":
    """Fetch all four data sources, build domain profiles, synthesize brief."""
    from uspto_client import fetch_patents, build_ip_portfolio
    from courtlistener_client import fetch_cases, build_litigation_profile
    from edgar_client import fetch_regulatory_data, build_regulatory_exposure
    from contracts_client import fetch_awards, build_contract_profile
    from brief_engine import build_brief
    from brief_generator import generate_brief

    patents   = fetch_patents(company, demo_mode=demo)
    cases     = fetch_cases(company, demo_mode=demo)
    reg_raw   = fetch_regulatory_data(company, ticker, demo_mode=demo)
    awards    = fetch_awards(company, demo_mode=demo)

    ip   = build_ip_portfolio(company, patents)
    lit  = build_litigation_profile(company, cases)
    reg  = build_regulatory_exposure(company, ticker, reg_raw)
    cont = build_contract_profile(company, awards)

    full_text, questions, summary = generate_brief(
        company, ticker, ip, lit, reg, cont, demo_mode=demo,
    )
    return build_brief(company, ticker, ip, lit, reg, cont, full_text, questions, summary)


@click.group()
@click.option("--demo/--live", default=True, help="Use demo data (default) or live APIs")
@click.pass_context
def cli(ctx: click.Context, demo: bool) -> None:
    """Pre-Acquisition Intelligence Brief Generator (P61)

    Generates structured intelligence briefs covering IP portfolio,
    litigation history, regulatory exposure, and contract dependency.
    """
    ctx.ensure_object(dict)
    ctx.obj["demo"] = demo


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.option("--ticker", default=DEMO_TICKER, help="Stock ticker symbol")
@click.pass_context
def brief(ctx: click.Context, company: str, ticker: str) -> None:
    """Generate a full pre-acquisition intelligence brief."""
    from dashboard import print_brief, print_brief_summary
    demo = ctx.obj.get("demo", True)
    with console.status(f"[cyan]Pulling intelligence on {company}...[/cyan]"):
        result = _run_pipeline(company, ticker, demo)
    print_brief_summary(result)
    print_brief(result)


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.pass_context
def ip(ctx: click.Context, company: str) -> None:
    """IP portfolio assessment — patent count, velocity, technology domains."""
    from uspto_client import fetch_patents, build_ip_portfolio
    from dashboard import print_ip_portfolio
    demo = ctx.obj.get("demo", True)
    patents = fetch_patents(company, demo_mode=demo)
    portfolio = build_ip_portfolio(company, patents)
    print_ip_portfolio(portfolio)


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.pass_context
def litigation(ctx: click.Context, company: str) -> None:
    """Litigation risk profile — active suits, IP disputes, regulatory actions."""
    from courtlistener_client import fetch_cases, build_litigation_profile
    from dashboard import print_litigation
    demo = ctx.obj.get("demo", True)
    cases = fetch_cases(company, demo_mode=demo)
    profile = build_litigation_profile(company, cases)
    print_litigation(profile)


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.option("--ticker", default=DEMO_TICKER)
@click.pass_context
def regulatory(ctx: click.Context, company: str, ticker: str) -> None:
    """Regulatory exposure flags — EDGAR material weakness, going concern, export controls."""
    from edgar_client import fetch_regulatory_data, build_regulatory_exposure
    from dashboard import print_regulatory
    demo = ctx.obj.get("demo", True)
    raw = fetch_regulatory_data(company, ticker, demo_mode=demo)
    exposure = build_regulatory_exposure(company, ticker, raw)
    print_regulatory(exposure)


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.pass_context
def contracts(ctx: click.Context, company: str) -> None:
    """Government contract dependency — agency breakdown, award history, NAICS."""
    from contracts_client import fetch_awards, build_contract_profile
    from dashboard import print_contracts
    demo = ctx.obj.get("demo", True)
    awards = fetch_awards(company, demo_mode=demo)
    profile = build_contract_profile(company, awards)
    print_contracts(profile)


@cli.command()
@click.argument("company", default=DEMO_COMPANY)
@click.option("--ticker", default=DEMO_TICKER)
@click.option("--format", "fmt", type=click.Choice(["json", "text"]), default="json")
@click.pass_context
def export(ctx: click.Context, company: str, ticker: str, fmt: str) -> None:
    """Export full brief as JSON or text."""
    demo = ctx.obj.get("demo", True)
    result = _run_pipeline(company, ticker, demo)
    if fmt == "text":
        filename = f"{company.replace(' ', '_').lower()}_brief.txt"
        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(result.full_text)
        console.print(f"[green]Exported to {filename}[/green]")
    else:
        import dataclasses
        filename = f"{company.replace(' ', '_').lower()}_brief.json"
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(dataclasses.asdict(result), fh, indent=2)
        console.print(f"[green]Exported to {filename}[/green]")


@cli.command()
def demo() -> None:
    """Run a full demonstration of all features using Parsons Corporation demo data."""
    from dashboard import (
        print_ip_portfolio, print_litigation, print_regulatory,
        print_contracts, print_brief_summary, print_brief,
    )
    from config import DEMO_COMPANY, DEMO_TICKER

    result = _run_pipeline(DEMO_COMPANY, DEMO_TICKER, demo=True)

    console.rule("[bold cyan]P61 — Pre-Acquisition Intelligence Brief Generator[/bold cyan]")
    console.print(f"[dim]Demo target: {DEMO_COMPANY} (NYSE: {DEMO_TICKER}) — "
                  f"mid-size defense IT / cybersecurity integrator[/dim]\n")

    console.rule("[bold]1 · IP Portfolio[/bold]")
    print_ip_portfolio(result.ip_portfolio)

    console.rule("[bold]2 · Litigation History[/bold]")
    print_litigation(result.litigation_profile)

    console.rule("[bold]3 · Regulatory Exposure[/bold]")
    print_regulatory(result.regulatory_exposure)

    console.rule("[bold]4 · Contract Dependency[/bold]")
    print_contracts(result.contract_profile)

    console.rule("[bold]5 · Full Brief[/bold]")
    print_brief_summary(result)
    print_brief(result)

    console.rule("[bold]6 · Brief Engine — Risk Tiers[/bold]")
    from brief_engine import (
        _ip_to_risk, _lit_to_risk, _reg_to_risk, _con_to_risk, compute_overall_risk,
    )
    ip  = result.ip_portfolio
    lit = result.litigation_profile
    reg = result.regulatory_exposure
    con = result.contract_profile
    console.print(f"  IP strength -> {ip.strength_tier} -> risk [{_ip_to_risk(ip.strength_tier)}]")
    console.print(f"  Litigation  -> {lit.risk_tier} -> risk [{_lit_to_risk(lit.risk_tier)}]")
    console.print(f"  Regulatory  -> {reg.exposure_tier} -> risk [{_reg_to_risk(reg.exposure_tier)}]")
    console.print(f"  Contracts   -> {con.dependency_tier} -> risk [{_con_to_risk(con.dependency_tier)}]")
    console.print(f"  Overall     -> [bold]{result.overall_risk_tier}[/bold]")

    console.rule("[bold]7 · Diligence Questions[/bold]")
    for i, q in enumerate(result.diligence_questions[:5], 1):
        console.print(f"  {i}. {q[:120]}")

    console.rule("[dim]Demo complete[/dim]")


if __name__ == "__main__":
    cli()
