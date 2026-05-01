{
  "brand": {
    "name": "NodeForge Dashboard",
    "design_personality": [
      "confident",
      "terminal-adjacent (but modern)",
      "high-density without clutter",
      "ops-grade clarity",
      "dark, professional fintech"
    ],
    "north_star": "Linear cleanliness + Bloomberg density + Vercel polish. No transparency; layered dark surfaces; crisp borders; mono numerics; semantic status pills."
  },

  "layout": {
    "page_structure": {
      "route": "/",
      "pattern": "single-page ops console",
      "header": "sticky top header with brand + live ticker chips + global actions (settings)",
      "body": "12-col grid on desktop; stacked cards on mobile",
      "density_modes": {
        "default": "comfortable",
        "optional_future": "compact toggle (not required for MVP)"
      }
    },
    "grid": {
      "container": "max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8",
      "desktop_columns": "grid grid-cols-12 gap-4 lg:gap-6",
      "card_spacing": "space-y-4 lg:space-y-6",
      "panel_radius": "rounded-xl",
      "panel_border": "border border-[hsl(var(--border))]"
    },
    "recommended_panel_spans_desktop": {
      "kpi_row": "col-span-12",
      "earnings_chart": "col-span-8",
      "ai_insights": "col-span-4",
      "nodes_table": "col-span-12",
      "wallets": "col-span-7",
      "auto_withdrawal": "col-span-5"
    },
    "responsive_rules": {
      "mobile": "everything stacks; header becomes 2-row; ticker chips horizontally scrollable",
      "tablet": "chart + insights become stacked if width < 1024px",
      "desktop": "keep chart + insights side-by-side; table full width"
    }
  },

  "typography": {
    "font_pairing": {
      "ui": {
        "name": "Space Grotesk",
        "google_fonts": "https://fonts.google.com/specimen/Space+Grotesk",
        "usage": "headings, labels, navigation, body"
      },
      "mono": {
        "name": "IBM Plex Mono",
        "google_fonts": "https://fonts.google.com/specimen/IBM+Plex+Mono",
        "usage": "all numeric values, tickers, addresses, timestamps"
      }
    },
    "tailwind_usage": {
      "headings": "font-[var(--font-ui)] tracking-[-0.02em]",
      "body": "font-[var(--font-ui)]",
      "numbers": "font-[var(--font-mono)] tabular-nums"
    },
    "type_scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold",
      "h2": "text-base md:text-lg font-medium text-muted-foreground",
      "section_title": "text-sm font-medium tracking-wide text-foreground",
      "kpi_value": "text-2xl sm:text-3xl font-semibold",
      "table": "text-sm",
      "micro": "text-xs text-muted-foreground"
    },
    "content_rules": {
      "avoid_centered_paragraphs": true,
      "truncate": "use truncate for long node names and addresses; provide tooltip/hover-card for full value"
    }
  },

  "color_system": {
    "mode": "dark-first (no transparent backgrounds)",
    "tokens_css": {
      "where": "/app/frontend/src/index.css",
      "instructions": "Replace :root and .dark tokens with this system; keep shadcn variable names but change values. Use HSL values (space-separated) as shadcn expects."
    },
    "core_tokens": {
      "background": "222 18% 7%",
      "foreground": "210 20% 96%",
      "card": "222 18% 9%",
      "card-foreground": "210 20% 96%",
      "popover": "222 18% 9%",
      "popover-foreground": "210 20% 96%",

      "primary": "168 62% 44%",
      "primary-foreground": "222 18% 7%",

      "secondary": "222 14% 14%",
      "secondary-foreground": "210 20% 96%",

      "muted": "222 14% 12%",
      "muted-foreground": "215 14% 70%",

      "accent": "222 14% 14%",
      "accent-foreground": "210 20% 96%",

      "destructive": "0 72% 52%",
      "destructive-foreground": "210 20% 96%",

      "border": "222 12% 18%",
      "input": "222 12% 18%",
      "ring": "168 62% 44%",

      "radius": "0.75rem",

      "chart-1": "168 62% 44%",
      "chart-2": "142 62% 48%",
      "chart-3": "38 92% 56%",
      "chart-4": "200 78% 52%",
      "chart-5": "280 62% 62%"
    },
    "semantic_status": {
      "healthy": {
        "fg": "142 62% 70%",
        "bg": "142 40% 14%",
        "border": "142 40% 22%"
      },
      "warning": {
        "fg": "38 92% 70%",
        "bg": "38 60% 14%",
        "border": "38 60% 22%"
      },
      "offline": {
        "fg": "0 72% 72%",
        "bg": "0 50% 14%",
        "border": "0 50% 22%"
      },
      "info": {
        "fg": "200 78% 72%",
        "bg": "200 50% 14%",
        "border": "200 50% 22%"
      }
    },
    "ticker_change_colors": {
      "positive": "text-[hsl(142_62%_70%)]",
      "negative": "text-[hsl(0_72%_72%)]",
      "neutral": "text-muted-foreground"
    },
    "gradient_policy": {
      "allowed": "Only subtle decorative overlays in hero/header area; max 20% viewport; never on cards or tables.",
      "recommended_gradient": "bg-[radial-gradient(60%_60%_at_20%_0%,hsl(168_62%_44%/0.18)_0%,transparent_60%),radial-gradient(50%_50%_at_80%_10%,hsl(200_78%_52%/0.12)_0%,transparent_55%)]",
      "note": "No purple/pink saturated gradients; keep overlays mild and sparse."
    }
  },

  "design_tokens": {
    "css_custom_properties": {
      "add_to_index_css": [
        "--font-ui: 'Space Grotesk', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji';",
        "--font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;",
        "--shadow-elev-1: 0 1px 0 hsl(0 0% 100% / 0.04), 0 10px 30px hsl(0 0% 0% / 0.35);",
        "--shadow-elev-2: 0 1px 0 hsl(0 0% 100% / 0.06), 0 18px 50px hsl(0 0% 0% / 0.45);",
        "--focus-ring: 0 0 0 3px hsl(var(--ring) / 0.35);",
        "--panel-padding: 1rem;",
        "--panel-padding-lg: 1.25rem;"
      ]
    },
    "spacing": {
      "rule": "Use 2–3x more spacing than feels comfortable; prefer whitespace over borders.",
      "panel_padding": "p-4 lg:p-5",
      "section_gap": "gap-4 lg:gap-6",
      "kpi_gap": "gap-3"
    },
    "radius": {
      "card": "rounded-xl",
      "chip": "rounded-full",
      "button": "rounded-md"
    }
  },

  "components": {
    "component_path": {
      "shadcn_primary": "/app/frontend/src/components/ui/",
      "use_components": {
        "header": ["badge.jsx", "button.jsx", "separator.jsx", "tooltip.jsx", "sheet.jsx"],
        "kpis": ["card.jsx", "badge.jsx", "separator.jsx", "skeleton.jsx"],
        "chart": ["card.jsx", "tabs.jsx", "tooltip.jsx", "skeleton.jsx"],
        "table": ["table.jsx", "badge.jsx", "dropdown-menu.jsx", "hover-card.jsx", "scroll-area.jsx"],
        "ai_insights": ["card.jsx", "button.jsx", "skeleton.jsx", "alert.jsx"],
        "wallets": ["card.jsx", "button.jsx", "separator.jsx", "tooltip.jsx"],
        "auto_withdrawal": ["card.jsx", "button.jsx", "dialog.jsx", "table.jsx", "badge.jsx"],
        "settings": ["sheet.jsx", "tabs.jsx", "form.jsx", "input.jsx", "label.jsx", "switch.jsx", "textarea.jsx", "alert.jsx"]
      }
    },
    "panel_specs": {
      "top_header": {
        "layout": "sticky top-0 z-40 border-b bg-background/?? (NO transparency) -> use bg-[hsl(var(--background))]",
        "structure": [
          "Left: NodeForge wordmark + small status dot",
          "Center: ticker chips row (scrollable on mobile)",
          "Right: last refresh time + Refresh icon button + Settings button"
        ],
        "ticker_chip": {
          "base": "inline-flex items-center gap-2 px-3 py-1.5 rounded-full border bg-card",
          "symbol": "text-xs font-medium text-muted-foreground",
          "price": "text-sm font-[var(--font-mono)] tabular-nums",
          "change": "text-xs font-[var(--font-mono)] tabular-nums",
          "interaction": "hover: border brightens; tooltip shows 24h high/low"
        },
        "data_testids": {
          "settings_button": "header-open-settings-button",
          "refresh_button": "header-refresh-button",
          "ticker_row": "header-ticker-row"
        }
      },

      "kpi_row": {
        "pattern": "bento KPI cards (6 cards) with consistent internal grid",
        "card": {
          "class": "rounded-xl border bg-card shadow-[var(--shadow-elev-1)]",
          "header": "label + optional delta badge",
          "value": "mono numeric; large",
          "sub": "micro text for secondary unit (USD + MYST)"
        },
        "kpis": [
          "Earnings 24h",
          "Earnings 30d",
          "Projected Annual",
          "Lifetime",
          "Nodes Online (X/Y)",
          "Next Auto-Withdrawal (countdown)"
        ],
        "data_testids": {
          "kpi_earnings_24h": "kpi-earnings-24h",
          "kpi_earnings_30d": "kpi-earnings-30d",
          "kpi_projected_annual": "kpi-earnings-projected-annual",
          "kpi_lifetime": "kpi-earnings-lifetime",
          "kpi_nodes_online": "kpi-nodes-online",
          "kpi_next_withdrawal": "kpi-next-auto-withdrawal"
        }
      },

      "earnings_chart": {
        "chart_type": "recharts AreaChart + Line overlay",
        "visual": {
          "area_fill": "hsl(var(--chart-1) / 0.18)",
          "line": "hsl(var(--chart-1))",
          "grid": "stroke: hsl(var(--border)); strokeDasharray: '3 3'",
          "tooltip": "shadcn Tooltip-like card with mono numbers"
        },
        "controls": {
          "timeframe_tabs": ["7d", "30d", "90d"],
          "currency_toggle": ["USD", "MYST"]
        },
        "data_testids": {
          "chart_panel": "earnings-chart-panel",
          "chart_timeframe_tabs": "earnings-chart-timeframe-tabs",
          "chart_currency_toggle": "earnings-chart-currency-toggle"
        }
      },

      "nodes_table": {
        "table_density": "compact rows; sticky header; horizontal scroll on small screens",
        "columns": [
          "Node",
          "Status (pill)",
          "Services",
          "24h Sessions",
          "30d Earnings",
          "Quality",
          "Last Seen",
          "Country",
          "Tailscale"
        ],
        "status_pill": {
          "healthy": "bg-[hsl(142_40%_14%)] text-[hsl(142_62%_70%)] border border-[hsl(142_40%_22%)]",
          "warning": "bg-[hsl(38_60%_14%)] text-[hsl(38_92%_70%)] border border-[hsl(38_60%_22%)]",
          "offline": "bg-[hsl(0_50%_14%)] text-[hsl(0_72%_72%)] border border-[hsl(0_50%_22%)]"
        },
        "row_interactions": {
          "hover": "row bg shifts to muted; show quick actions (copy node id, open logs) via ghost buttons",
          "click": "optional: open node detail dialog (future)"
        },
        "data_testids": {
          "nodes_table": "nodes-table",
          "nodes_table_row": "nodes-table-row",
          "nodes_table_status_pill": "nodes-table-status-pill"
        }
      },

      "ai_insights": {
        "tone": "succinct bullets; actionable; show estimated revenue impact",
        "layout": "Card with header: 'AI Insights' + Refresh button; body: list with icons",
        "empty_state": "Explain what insights are and show 'Generate insights' CTA",
        "data_testids": {
          "ai_insights_panel": "ai-insights-panel",
          "ai_insights_refresh": "ai-insights-refresh-button"
        }
      },

      "wallets_card": {
        "layout": "Two wallet blocks; each shows address (mono), balances grid, explorer link",
        "address_display": "truncate + copy button; hover-card reveals full address",
        "data_testids": {
          "wallets_panel": "wallets-panel",
          "wallet_address": "wallet-address",
          "wallet_explorer_link": "wallet-explorer-link"
        }
      },

      "auto_withdrawal_panel": {
        "layout": "Countdown + threshold + Run now button + recent log preview",
        "run_now": "Primary button; confirm via AlertDialog",
        "log_dialog": "Dialog with Table + filters",
        "data_testids": {
          "auto_withdrawal_panel": "auto-withdrawal-panel",
          "auto_withdrawal_run_now": "auto-withdrawal-run-now-button",
          "auto_withdrawal_log_open": "auto-withdrawal-open-log-button"
        }
      },

      "settings_drawer": {
        "component": "Sheet (right side)",
        "tabs": ["Accounts", "Automation", "Advanced"],
        "fields": [
          "Mystnodes email/password",
          "Tailscale API key",
          "Withdrawal threshold",
          "Notification preferences"
        ],
        "security": "Password inputs masked; show 'Test connection' buttons",
        "data_testids": {
          "settings_drawer": "settings-drawer",
          "settings_save": "settings-save-button",
          "settings_test_mystnodes": "settings-test-mystnodes-button",
          "settings_test_tailscale": "settings-test-tailscale-button"
        }
      }
    },

    "buttons": {
      "style": "Professional / Corporate",
      "variants": {
        "primary": "bg-primary text-primary-foreground hover:bg-[hsl(var(--primary)/0.9)] focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]",
        "secondary": "bg-secondary text-secondary-foreground hover:bg-[hsl(var(--secondary)/0.85)]",
        "ghost": "bg-transparent hover:bg-muted"
      },
      "motion": "hover: subtle translateY(-1px) + shadow increase; active: scale(0.98)",
      "no_transition_all": true
    }
  },

  "motion": {
    "principles": [
      "Subtle, fast, purposeful",
      "Prefer opacity + shadow + border-color transitions",
      "Avoid layout shift"
    ],
    "micro_interactions": {
      "buttons": "transition-colors duration-150; active:scale-[0.98]",
      "cards": "hover:shadow-[var(--shadow-elev-2)] hover:border-[hsl(var(--border)/0.8)]",
      "table_rows": "hover:bg-muted/?? (NO transparency) -> use hover:bg-[hsl(var(--muted))]",
      "ticker": "price flash on update: briefly apply bg info tint for 250ms"
    },
    "library": {
      "recommended": "framer-motion",
      "install": "npm i framer-motion",
      "usage": "Animate panel entrance (y: 6 -> 0, opacity: 0 -> 1), and ticker update flashes. Respect prefers-reduced-motion."
    }
  },

  "data_density_patterns": {
    "numbers": {
      "rule": "Always use mono + tabular-nums; align right in tables; show units as muted micro text.",
      "formatting": "Use Intl.NumberFormat; show $ with 2 decimals for USD; MYST with 3-4 decimals; timestamps relative + tooltip absolute."
    },
    "badges": {
      "use": "Status, service types, deltas",
      "style": "outlined badges for services; filled semantic pills for status"
    }
  },

  "empty_loading_error_states": {
    "loading": {
      "pattern": "Use shadcn Skeleton blocks matching final layout; avoid spinners-only.",
      "data_testid": "panel-loading-skeleton"
    },
    "empty": {
      "pattern": "Card with icon + 1 sentence + primary CTA (e.g., Connect account in Settings)",
      "copy_examples": {
        "nodes": "No nodes yet. Connect Mystnodes to start monitoring.",
        "insights": "Generate insights to spot underperformance and revenue leaks."
      },
      "data_testid": "panel-empty-state"
    },
    "error": {
      "pattern": "Use shadcn Alert (destructive) with retry button; include error code in mono small text.",
      "data_testid": "panel-error-state"
    }
  },

  "icons": {
    "library": "lucide-react",
    "usage": {
      "status": ["CheckCircle2", "AlertTriangle", "XCircle"],
      "actions": ["RefreshCw", "Settings", "ExternalLink", "Copy", "Play", "Clock"],
      "tables": ["ChevronDown", "ArrowUpRight", "ArrowDownRight"]
    },
    "rules": "No emoji icons. Keep stroke-1.5 or stroke-2 consistent."
  },

  "charts": {
    "recharts_guidelines": {
      "theme": "Use CSS variables for stroke/fill; tooltip uses Card styles; axis ticks muted.",
      "empty_state": "Show flatline placeholder + 'No earnings data for selected range'",
      "accessibility": "Provide aria-labels for chart container; ensure tooltip content is keyboard reachable if possible."
    }
  },

  "accessibility": {
    "contrast": "Maintain WCAG AA; avoid pure black (#000) and pure white (#fff) for large areas.",
    "focus": "Visible focus ring using --focus-ring; never remove outline without replacement.",
    "reduced_motion": "Respect prefers-reduced-motion; disable entrance animations and ticker flashes.",
    "keyboard": "All dialogs/sheets/tabs navigable via keyboard (shadcn defaults)."
  },

  "image_urls": {
    "decorative_backgrounds": [
      {
        "url": "https://images.unsplash.com/photo-1599104040457-fe0e8c9ae77e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwzfHxkYXJrJTIwYWJzdHJhY3QlMjBncmlkJTIwdGV4dHVyZSUyMGJhY2tncm91bmR8ZW58MHx8fHRlYWx8MTc3NzYxMTg0NXww&ixlib=rb-4.1.0&q=85",
        "category": "header-overlay",
        "description": "Use as a very subtle header background texture (opacity 0.06–0.10) behind ticker row only; do not place behind tables/cards."
      },
      {
        "url": "https://images.pexels.com/photos/4065437/pexels-photo-4065437.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "category": "empty-state-illustration",
        "description": "Use as a blurred/zoomed abstract texture in empty states (opacity 0.08) to avoid flatness."
      }
    ]
  },

  "implementation_notes_js": {
    "react_files": "Project uses .js (not .tsx). Keep components in JS; use prop-types only if already used; otherwise rely on runtime checks.",
    "data_testid_rule": "Every interactive element and key informational element must include data-testid in kebab-case describing role.",
    "no_transparency_rule": "Do not use bg-background/50 or backdrop-blur; use solid bg tokens only.",
    "remove_default_centering": "Do not use .App { text-align: center }. Remove CRA demo styles from App.css; rely on Tailwind layout."
  },

  "instructions_to_main_agent": [
    "1) Update /app/frontend/src/index.css tokens to the provided dark-first HSL values; set body font-family to var(--font-ui) and numeric spans to var(--font-mono).",
    "2) Delete CRA demo styles in /app/frontend/src/App.css (App-header centering, logo spin).",
    "3) Build the dashboard using shadcn Card/Table/Badge/Sheet/Dialog/Tabs/Skeleton; keep panels solid (no transparency).",
    "4) Apply mono + tabular-nums to all numeric values and right-align numeric table columns.",
    "5) Implement semantic status pills using the provided bg/fg/border classes; use lucide-react icons.",
    "6) Add data-testid attributes everywhere required (buttons, inputs, tabs, table rows, KPI values, error/empty states).",
    "7) Use recharts for earnings chart with CSS-variable-driven colors; tooltip styled as Card.",
    "8) Add subtle motion with framer-motion (optional) and ensure prefers-reduced-motion compliance."
  ]
}

---

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
