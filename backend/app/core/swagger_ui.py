"""
Custom Swagger UI with high-contrast, accessible themes for XPort REST API.
Provides both an ultra-readable Dark theme (matching XPort's dark glassmorphism aesthetic)
and a High-Contrast Light theme with an interactive theme toggle in the top bar.
"""

from fastapi.responses import HTMLResponse


def get_custom_swagger_ui_html(
    *,
    openapi_url: str,
    title: str = "XPort API Documentation",
    version: str = "0.1.0",
) -> HTMLResponse:
    """
    Renders an accessible, beautifully themed Swagger UI HTML document
    with dark/light theme switching and high contrast readability.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        /* ==========================================================================
           XPort Swagger UI Design System & High-Contrast Readability Engine
           ========================================================================== */

        :root,
        [data-theme="dark"] {{
            color-scheme: dark;
            --xp-bg-canvas: #0B0F19;
            --xp-bg-surface: #111827;
            --xp-bg-card: #131B2E;
            --xp-bg-card-header: #1E293B;
            --xp-bg-subtle: rgba(255, 255, 255, 0.03);
            --xp-bg-input: #1E293B;
            --xp-bg-code: #070A12;

            --xp-border-subtle: rgba(255, 255, 255, 0.08);
            --xp-border-input: #475569;
            --xp-border-focus: #3B82F6;

            --xp-text-primary: #F8FAFC;
            --xp-text-secondary: #CBD5E1;
            --xp-text-muted: #94A3B8;
            --xp-text-code: #E2E8F0;

            --xp-primary: #3B82F6;
            --xp-primary-hover: #2563EB;
            --xp-primary-glow: rgba(59, 130, 246, 0.25);

            --xp-get-bg: rgba(16, 185, 129, 0.09);
            --xp-get-border: rgba(16, 185, 129, 0.35);
            --xp-get-badge: #059669;
            --xp-get-text: #6EE7B7;

            --xp-post-bg: rgba(59, 130, 246, 0.09);
            --xp-post-border: rgba(59, 130, 246, 0.35);
            --xp-post-badge: #2563EB;
            --xp-post-text: #93C5FD;

            --xp-put-bg: rgba(245, 158, 11, 0.09);
            --xp-put-border: rgba(245, 158, 11, 0.35);
            --xp-put-badge: #D97706;
            --xp-put-text: #FCD34D;

            --xp-delete-bg: rgba(239, 68, 68, 0.09);
            --xp-delete-border: rgba(239, 68, 68, 0.35);
            --xp-delete-badge: #DC2626;
            --xp-delete-text: #FCA5A5;

            --xp-patch-bg: rgba(168, 85, 247, 0.09);
            --xp-patch-border: rgba(168, 85, 247, 0.35);
            --xp-patch-badge: #9333EA;
            --xp-patch-text: #D8B4FE;

            --xp-topbar-bg: #0F172A;
            --xp-topbar-border: rgba(255, 255, 255, 0.1);
        }}

        [data-theme="light"] {{
            color-scheme: light;
            --xp-bg-canvas: #F8FAFC;
            --xp-bg-surface: #FFFFFF;
            --xp-bg-card: #FFFFFF;
            --xp-bg-card-header: #F1F5F9;
            --xp-bg-subtle: rgba(15, 23, 42, 0.03);
            --xp-bg-input: #FFFFFF;
            --xp-bg-code: #0F172A;

            --xp-border-subtle: rgba(15, 23, 42, 0.1);
            --xp-border-input: #CBD5E1;
            --xp-border-focus: #2563EB;

            --xp-text-primary: #0F172A;
            --xp-text-secondary: #334155;
            --xp-text-muted: #64748B;
            --xp-text-code: #F8FAFC;

            --xp-primary: #2563EB;
            --xp-primary-hover: #1D4ED8;
            --xp-primary-glow: rgba(37, 99, 235, 0.15);

            --xp-get-bg: rgba(16, 185, 129, 0.07);
            --xp-get-border: rgba(16, 185, 129, 0.4);
            --xp-get-badge: #059669;
            --xp-get-text: #065F46;

            --xp-post-bg: rgba(59, 130, 246, 0.07);
            --xp-post-border: rgba(59, 130, 246, 0.4);
            --xp-post-badge: #2563EB;
            --xp-post-text: #1E40AF;

            --xp-put-bg: rgba(245, 158, 11, 0.07);
            --xp-put-border: rgba(245, 158, 11, 0.4);
            --xp-put-badge: #D97706;
            --xp-put-text: #92400E;

            --xp-delete-bg: rgba(239, 68, 68, 0.07);
            --xp-delete-border: rgba(239, 68, 68, 0.4);
            --xp-delete-badge: #DC2626;
            --xp-delete-text: #991B1B;

            --xp-patch-bg: rgba(168, 85, 247, 0.07);
            --xp-patch-border: rgba(168, 85, 247, 0.4);
            --xp-patch-badge: #9333EA;
            --xp-patch-text: #6B21A8;

            --xp-topbar-bg: #FFFFFF;
            --xp-topbar-border: rgba(15, 23, 42, 0.1);
        }}

        /* Base Reset & Fonts */
        *, *::before, *::after {{
            box-sizing: border-box;
        }}

        body, html {{
            margin: 0;
            padding: 0;
            background-color: var(--xp-bg-canvas) !important;
            color: var(--xp-text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        /* Custom Modern Topbar */
        .xport-custom-header {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: var(--xp-topbar-bg);
            border-bottom: 1px solid var(--xp-topbar-border);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: background 0.25s ease, border-color 0.25s ease;
        }}

        .xport-brand {{
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
        }}

        .xport-brand-logo {{
            width: 34px;
            height: 34px;
            border-radius: 8px;
            background: linear-gradient(135deg, #2563EB 0%, #38BDF8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 16px;
            box-shadow: 0 0 16px rgba(37, 99, 235, 0.4);
        }}

        .xport-brand-text {{
            display: flex;
            flex-direction: column;
        }}

        .xport-brand-title {{
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--xp-text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .xport-version-badge {{
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 9999px;
            background: rgba(59, 130, 246, 0.15);
            color: var(--xp-primary);
            border: 1px solid rgba(59, 130, 246, 0.3);
            letter-spacing: 0;
        }}

        .xport-brand-subtitle {{
            font-size: 12px;
            color: var(--xp-text-muted);
            font-weight: 400;
        }}

        .xport-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .xport-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            color: var(--xp-text-secondary);
            background: var(--xp-bg-subtle);
            border: 1px solid var(--xp-border-subtle);
            transition: all 0.2s ease;
        }}

        .xport-link-btn:hover {{
            color: var(--xp-text-primary);
            border-color: var(--xp-primary);
            background: rgba(59, 130, 246, 0.1);
        }}

        .xport-theme-toggle {{
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: var(--xp-text-primary);
            background: var(--xp-bg-card);
            border: 1px solid var(--xp-border-subtle);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            transition: all 0.2s ease;
            user-select: none;
        }}

        .xport-theme-toggle:hover {{
            border-color: var(--xp-primary);
            box-shadow: 0 0 12px var(--xp-primary-glow);
            transform: translateY(-1px);
        }}

        /* Swagger UI Overrides */
        .swagger-ui {{
            color: var(--xp-text-primary) !important;
            font-family: inherit !important;
        }}

        /* Hide Default Swagger Header */
        .swagger-ui .topbar {{
            display: none !important;
        }}

        /* Main Container & Padding */
        .swagger-ui .wrapper {{
            max-width: 1380px !important;
            padding: 24px 20px !important;
        }}

        /* Info Section */
        .swagger-ui .info {{
            margin: 20px 0 32px 0 !important;
        }}

        .swagger-ui .info .title {{
            color: var(--xp-text-primary) !important;
            font-size: 32px !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
        }}

        .swagger-ui .info p,
        .swagger-ui .info li,
        .swagger-ui .info .description,
        .swagger-ui .info .description p {{
            color: var(--xp-text-secondary) !important;
            font-size: 14.5px !important;
            line-height: 1.65 !important;
        }}

        .swagger-ui .info a {{
            color: var(--xp-primary) !important;
            text-decoration: underline !important;
        }}

        .swagger-ui .info .base-url {{
            color: var(--xp-text-muted) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12.5px !important;
        }}

        /* Server / Scheme Container */
        .swagger-ui .scheme-container {{
            background: var(--xp-bg-card) !important;
            border: 1px solid var(--xp-border-subtle) !important;
            border-radius: 10px !important;
            padding: 16px 20px !important;
            margin-bottom: 28px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
        }}

        .swagger-ui .schemes-title {{
            color: var(--xp-text-primary) !important;
            font-weight: 600 !important;
        }}

        .swagger-ui .schemes > select {{
            background: var(--xp-bg-input) !important;
            color: var(--xp-text-primary) !important;
            border: 1px solid var(--xp-border-input) !important;
            border-radius: 6px !important;
            padding: 6px 12px !important;
            font-size: 13.5px !important;
        }}

        /* Filter Box */
        .swagger-ui .filter .operation-filter-input {{
            background: var(--xp-bg-input) !important;
            color: var(--xp-text-primary) !important;
            border: 1px solid var(--xp-border-input) !important;
            border-radius: 8px !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
            margin-bottom: 20px !important;
        }}

        .swagger-ui .filter .operation-filter-input:focus {{
            border-color: var(--xp-border-focus) !important;
            outline: none !important;
            box-shadow: 0 0 0 3px var(--xp-primary-glow) !important;
        }}

        /* Tag Headers */
        .swagger-ui .opblock-tag-section {{
            margin-bottom: 24px !important;
        }}

        .swagger-ui .opblock-tag {{
            color: var(--xp-text-primary) !important;
            border-bottom: 1px solid var(--xp-border-subtle) !important;
            padding: 12px 0 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }}

        .swagger-ui .opblock-tag:hover {{
            background: transparent !important;
        }}

        .swagger-ui .opblock-tag small {{
            color: var(--xp-text-muted) !important;
            font-size: 13px !important;
            font-weight: 400 !important;
        }}

        /* Operation Blocks (Endpoints) */
        .swagger-ui .opblock {{
            border-radius: 10px !important;
            margin: 0 0 16px 0 !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08) !important;
            overflow: hidden !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }}

        .swagger-ui .opblock:hover {{
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.14) !important;
        }}

        .swagger-ui .opblock .opblock-summary {{
            padding: 10px 16px !important;
        }}

        .swagger-ui .opblock .opblock-summary-method {{
            border-radius: 6px !important;
            font-weight: 700 !important;
            font-size: 12px !important;
            padding: 6px 14px !important;
            min-width: 80px !important;
            text-align: center !important;
            letter-spacing: 0.05em !important;
        }}

        .swagger-ui .opblock .opblock-summary-path,
        .swagger-ui .opblock .opblock-summary-path__deprecated {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            color: var(--xp-text-primary) !important;
        }}

        .swagger-ui .opblock .opblock-summary-description {{
            color: var(--xp-text-muted) !important;
            font-size: 13px !important;
            font-weight: 400 !important;
        }}

        /* Specific Method Palettes */
        .swagger-ui .opblock.opblock-get {{
            background: var(--xp-get-bg) !important;
            border: 1px solid var(--xp-get-border) !important;
        }}
        .swagger-ui .opblock.opblock-get .opblock-summary-method {{
            background: var(--xp-get-badge) !important;
            color: #FFFFFF !important;
        }}
        .swagger-ui .opblock.opblock-get .opblock-summary-path {{
            color: var(--xp-get-text) !important;
        }}

        .swagger-ui .opblock.opblock-post {{
            background: var(--xp-post-bg) !important;
            border: 1px solid var(--xp-post-border) !important;
        }}
        .swagger-ui .opblock.opblock-post .opblock-summary-method {{
            background: var(--xp-post-badge) !important;
            color: #FFFFFF !important;
        }}
        .swagger-ui .opblock.opblock-post .opblock-summary-path {{
            color: var(--xp-post-text) !important;
        }}

        .swagger-ui .opblock.opblock-put {{
            background: var(--xp-put-bg) !important;
            border: 1px solid var(--xp-put-border) !important;
        }}
        .swagger-ui .opblock.opblock-put .opblock-summary-method {{
            background: var(--xp-put-badge) !important;
            color: #FFFFFF !important;
        }}
        .swagger-ui .opblock.opblock-put .opblock-summary-path {{
            color: var(--xp-put-text) !important;
        }}

        .swagger-ui .opblock.opblock-delete {{
            background: var(--xp-delete-bg) !important;
            border: 1px solid var(--xp-delete-border) !important;
        }}
        .swagger-ui .opblock.opblock-delete .opblock-summary-method {{
            background: var(--xp-delete-badge) !important;
            color: #FFFFFF !important;
        }}
        .swagger-ui .opblock.opblock-delete .opblock-summary-path {{
            color: var(--xp-delete-text) !important;
        }}

        .swagger-ui .opblock.opblock-patch {{
            background: var(--xp-patch-bg) !important;
            border: 1px solid var(--xp-patch-border) !important;
        }}
        .swagger-ui .opblock.opblock-patch .opblock-summary-method {{
            background: var(--xp-patch-badge) !important;
            color: #FFFFFF !important;
        }}
        .swagger-ui .opblock.opblock-patch .opblock-summary-path {{
            color: var(--xp-patch-text) !important;
        }}

        /* Operation Body (Expanded State) */
        .swagger-ui .opblock-body {{
            background: var(--xp-bg-surface) !important;
            border-top: 1px solid var(--xp-border-subtle) !important;
            padding: 16px 20px !important;
        }}

        .swagger-ui .opblock-section-header {{
            background: var(--xp-bg-card-header) !important;
            border: 1px solid var(--xp-border-subtle) !important;
            border-radius: 6px !important;
            padding: 8px 14px !important;
            box-shadow: none !important;
        }}

        .swagger-ui .opblock-section-header h4 {{
            color: var(--xp-text-primary) !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
        }}

        .swagger-ui .opblock-description-wrapper p,
        .swagger-ui .opblock-title_normal p {{
            color: var(--xp-text-secondary) !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
        }}

        /* Parameters Table */
        .swagger-ui table.parameters {{
            border-collapse: collapse !important;
            width: 100% !important;
        }}

        .swagger-ui table thead tr th,
        .swagger-ui table thead tr td {{
            color: var(--xp-text-primary) !important;
            border-bottom: 2px solid var(--xp-border-subtle) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            padding: 10px 12px !important;
            background: transparent !important;
        }}

        .swagger-ui table tbody tr td {{
            color: var(--xp-text-secondary) !important;
            border-bottom: 1px solid var(--xp-border-subtle) !important;
            padding: 12px !important;
            vertical-align: top !important;
        }}

        .swagger-ui .parameter__name {{
            color: var(--xp-text-primary) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }}

        .swagger-ui .parameter__name.required:after {{
            color: #EF4444 !important;
            font-weight: 700 !important;
        }}

        .swagger-ui .parameter__type {{
            color: var(--xp-primary) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }}

        .swagger-ui .parameter__in {{
            color: var(--xp-text-muted) !important;
            font-size: 12px !important;
            font-style: italic !important;
        }}

        .swagger-ui .renderedMarkdown p {{
            color: var(--xp-text-secondary) !important;
            font-size: 13.5px !important;
            margin: 0 !important;
        }}

        /* Inputs, Textareas, Selects */
        .swagger-ui input[type=text],
        .swagger-ui input[type=password],
        .swagger-ui input[type=search],
        .swagger-ui input[type=number],
        .swagger-ui textarea,
        .swagger-ui select {{
            background: var(--xp-bg-input) !important;
            color: var(--xp-text-primary) !important;
            border: 1px solid var(--xp-border-input) !important;
            border-radius: 6px !important;
            padding: 8px 12px !important;
            font-size: 13px !important;
            outline: none !important;
            transition: all 0.2s ease !important;
        }}

        .swagger-ui input[type=text]:focus,
        .swagger-ui textarea:focus,
        .swagger-ui select:focus {{
            border-color: var(--xp-border-focus) !important;
            box-shadow: 0 0 0 3px var(--xp-primary-glow) !important;
        }}

        .swagger-ui select option {{
            background: var(--xp-bg-surface) !important;
            color: var(--xp-text-primary) !important;
        }}

        /* Buttons */
        .swagger-ui .btn {{
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            padding: 6px 14px !important;
            transition: all 0.2s ease !important;
        }}

        .swagger-ui .btn.try-out__btn {{
            background: var(--xp-bg-card) !important;
            color: var(--xp-primary) !important;
            border: 1px solid var(--xp-border-focus) !important;
        }}

        .swagger-ui .btn.try-out__btn:hover {{
            background: var(--xp-primary) !important;
            color: #FFFFFF !important;
        }}

        .swagger-ui .btn.execute {{
            background: var(--xp-primary) !important;
            border: 1px solid var(--xp-primary) !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 10px var(--xp-primary-glow) !important;
        }}

        .swagger-ui .btn.execute:hover {{
            background: var(--xp-primary-hover) !important;
        }}

        .swagger-ui .btn.btn-clear {{
            background: var(--xp-bg-card-header) !important;
            color: var(--xp-text-primary) !important;
            border: 1px solid var(--xp-border-subtle) !important;
        }}

        .swagger-ui .btn.cancel {{
            background: #DC2626 !important;
            border-color: #DC2626 !important;
            color: #FFFFFF !important;
        }}

        /* Responses */
        .swagger-ui .responses-inner h4,
        .swagger-ui .responses-inner h5 {{
            color: var(--xp-text-primary) !important;
            font-weight: 600 !important;
        }}

        .swagger-ui .response-col_status {{
            color: var(--xp-text-primary) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            font-size: 14px !important;
        }}

        .swagger-ui .response-col_description {{
            color: var(--xp-text-secondary) !important;
        }}

        .swagger-ui .response-col_description__inner div.markdown p {{
            color: var(--xp-text-secondary) !important;
        }}

        /* Code & Previews */
        .swagger-ui pre,
        .swagger-ui .highlight-code,
        .swagger-ui .microlight {{
            background: var(--xp-bg-code) !important;
            color: var(--xp-text-code) !important;
            border: 1px solid var(--xp-border-subtle) !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 13px !important;
            padding: 12px 16px !important;
        }}

        .swagger-ui code {{
            color: var(--xp-primary) !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}

        .swagger-ui .copy-to-clipboard {{
            background: var(--xp-bg-card-header) !important;
            border-radius: 6px !important;
        }}

        .swagger-ui .copy-to-clipboard button {{
            filter: invert(0.8) !important;
        }}

        /* Schemas / Models Section */
        .swagger-ui section.models {{
            background: var(--xp-bg-card) !important;
            border: 1px solid var(--xp-border-subtle) !important;
            border-radius: 10px !important;
            margin-top: 36px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        }}

        .swagger-ui section.models h4 {{
            color: var(--xp-text-primary) !important;
            border-bottom: 1px solid var(--xp-border-subtle) !important;
            padding: 14px 20px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
        }}

        .swagger-ui section.models .model-container {{
            background: var(--xp-bg-canvas) !important;
            border: 1px solid var(--xp-border-subtle) !important;
            border-radius: 8px !important;
            margin: 10px 16px !important;
            padding: 12px 16px !important;
        }}

        .swagger-ui .model-title {{
            color: var(--xp-primary) !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
        }}

        .swagger-ui .model {{
            color: var(--xp-text-primary) !important;
        }}

        .swagger-ui .model-box {{
            background: transparent !important;
        }}

        .swagger-ui .prop-type {{
            color: #A855F7 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12.5px !important;
        }}

        .swagger-ui .prop-format {{
            color: var(--xp-text-muted) !important;
        }}

        .swagger-ui .property-row td {{
            color: var(--xp-text-secondary) !important;
            border-bottom: 1px solid var(--xp-border-subtle) !important;
        }}

        .swagger-ui .model-toggle:after {{
            filter: invert(0.8) !important;
        }}

        .swagger-ui svg {{
            fill: var(--xp-text-muted) !important;
        }}

        .swagger-ui .arrow {{
            fill: var(--xp-text-muted) !important;
        }}

        .swagger-ui .loading-container .loading:after {{
            color: var(--xp-text-primary) !important;
        }}

        /* Scrollbars */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: var(--xp-bg-canvas);
        }}
        ::-webkit-scrollbar-thumb {{
            background: var(--xp-border-input);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--xp-primary);
        }}
    </style>
</head>
<body>
    <!-- Top Bar Navigation with Instant Theme Switcher -->
    <header class="xport-custom-header">
        <div class="xport-brand">
            <div class="xport-brand-logo">XP</div>
            <div class="xport-brand-text">
                <div class="xport-brand-title">
                    XPort API Documentation
                    <span class="xport-version-badge">v{version}</span>
                </div>
                <div class="xport-brand-subtitle">
                    Explainable Multi-Objective Portfolio Optimization Framework
                </div>
            </div>
        </div>
        <div class="xport-actions">
            <a href="{openapi_url}" target="_blank" class="xport-link-btn" title="Open raw OpenAPI schema">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
                OpenAPI Spec
            </a>
            <a href="/api/v1/health" target="_blank" class="xport-link-btn" title="Inspect system operational status">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
                Health Probe
            </a>
            <button id="themeToggleBtn" class="xport-theme-toggle" type="button" aria-label="Toggle color theme">
                <span id="themeToggleIcon">🌙</span>
                <span id="themeToggleLabel">Dark Theme</span>
            </button>
        </div>
    </header>

    <!-- Swagger UI Mount Point -->
    <div id="swagger-ui"></div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        // Theme Management Script
        (function() {{
            const STORAGE_KEY = 'xport_swagger_theme';
            const htmlEl = document.documentElement;
            const toggleBtn = document.getElementById('themeToggleBtn');
            const toggleIcon = document.getElementById('themeToggleIcon');
            const toggleLabel = document.getElementById('themeToggleLabel');

            function applyTheme(theme) {{
                htmlEl.setAttribute('data-theme', theme);
                localStorage.setItem(STORAGE_KEY, theme);
                if (theme === 'dark') {{
                    toggleIcon.textContent = '🌙';
                    toggleLabel.textContent = 'Dark Theme';
                    htmlEl.style.colorScheme = 'dark';
                }} else {{
                    toggleIcon.textContent = '☀️';
                    toggleLabel.textContent = 'Light Theme';
                    htmlEl.style.colorScheme = 'light';
                }}
            }}

            // Detect preferred or stored theme
            const savedTheme = localStorage.getItem(STORAGE_KEY);
            if (savedTheme) {{
                applyTheme(savedTheme);
            }} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {{
                applyTheme('light');
            }} else {{
                applyTheme('dark');
            }}

            toggleBtn.addEventListener('click', function() {{
                const current = htmlEl.getAttribute('data-theme') || 'dark';
                applyTheme(current === 'dark' ? 'light' : 'dark');
            }});
        }})();

        // Initialize Swagger UI Bundle
        window.onload = () => {{
            window.ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                filter: true,
                displayRequestDuration: true,
                persistAuthorization: true,
                docExpansion: "list",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1
            }});
        }};
    </script>
</body>
</html>
"""
    return HTMLResponse(html_content)
