"""Sources de news (flux RSS / Atom)."""

from .rss import analyser_flux_xml, recuperer_flux

__all__ = ["analyser_flux_xml", "recuperer_flux"]
