-- Wangan yoru look and feel.
-- The Shutoko expressway at night: blue is the
-- body, amber is the instruments, red is the redline only. Every shape is round.
-- The focused window's 1px border carries the paint shift (purple, blue, bronze
-- green) and a blue glow sits behind it; the others get a hairline. Loaded after
-- futuwwa.lua so these values win; behaviour and binds stay there.
-- The popups and helpers are shared by both Wangan variants (wangan-*).

local C = {
    ground = "0B0D11",
    line   = "2A323F",
    purple = "6A4BC4",
    blue   = "3D74DD",
    green  = "4C9A80",
    glow   = "2A5FC4",
}

hl.config({
    general = {
        gaps_in     = 6,
        gaps_out    = 14,
        border_size = 1,
        col = {
            active_border   = {
                colors = { "rgb(" .. C.purple .. ")", "rgb(" .. C.blue .. ")", "rgb(" .. C.green .. ")" },
                angle  = 45,
            },
            inactive_border = "rgb(" .. C.line .. ")",
        },
    },

    decoration = {
        rounding       = 10,
        rounding_power = 2.0,

        active_opacity   = 0.95,
        inactive_opacity = 0.88,

        blur = {
            enabled           = true,
            size              = 8,
            passes            = 3,
            vibrancy          = 0.10,
            noise             = 0.01,
            new_optimizations = true,
            popups            = true,
        },

        glow = {
            enabled = false,
        },

        -- The light trail: a blue glow behind the focused window only.
        shadow = {
            enabled        = true,
            range          = 22,
            render_power   = 3,
            offset         = { 0, 0 },
            color          = "rgba(" .. C.glow .. "59)",
            color_inactive = "rgba(00000099)",
        },
    },

    group = {
        col = {
            border_active   = "rgb(" .. C.blue .. ")",
            border_inactive = "rgb(" .. C.line .. ")",
        },
    },

    misc = {
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
        background_color         = "rgb(" .. C.ground .. ")",
    },
})

-- Cursor: WanganYoruNeedle (~/.local/share/icons/WanganYoruNeedle, hyprcursor + XCursor).
-- On a live theme switch restore.sh runs `hyprctl setcursor` from gsettings.txt.
hl.env("HYPRCURSOR_THEME", "WanganYoruNeedle")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "WanganYoruNeedle")
hl.env("XCURSOR_SIZE", "24")

-- A config reload resets the cursor to the default theme; set it again.
local function wangan_cursor()
    hl.exec_cmd("hyprctl setcursor WanganYoruNeedle 24")
end
hl.on("hyprland.start", wangan_cursor)
hl.on("config.reloaded", wangan_cursor)

-- Launcher bind points at the Wangan launcher; futuwwa.lua binds the Girih one.
hl.unbind("SUPER + D")
hl.bind("SUPER + D",
    hl.dsp.exec_cmd(os.getenv("HOME") .. "/.local/bin/wangan-launcher"),
    { description = "Application launcher" })

-- Terminals draw their own glass (foot/alacritty/ghostty alpha) so text stays opaque.
hl.window_rule({
    name    = "wangan-terminal-opaque",
    match   = { class = "^(foot|footclient|Alacritty|com.mitchellh.ghostty)$" },
    opacity = "1.0 override 1.0 override",
})

-- Blur behind layer surfaces: the bar, alert banners, launcher, notifications.
-- ignore_alpha keeps fully transparent parts of a layer unblurred.
hl.layer_rule({
    name         = "wangan-bar-glass",
    match        = { namespace = "^hattin-" },
    blur         = true,
    ignore_alpha = 0.1,
})

hl.layer_rule({
    name         = "wangan-launcher-glass",
    match        = { namespace = "^launcher$" },
    blur         = true,
    ignore_alpha = 0.1,
})

hl.layer_rule({
    name         = "wangan-notify-glass",
    match        = { namespace = "^swaync" },
    blur         = true,
    ignore_alpha = 0.1,
})

-- Launcher: floating foot + fzf (~/.local/bin/wangan-launcher).
hl.window_rule({
    name     = "wangan-launcher",
    match    = { class = "^wangan-launcher$" },
    float    = true,
    size     = "780 470",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

-- Taskwarrior popups from the waybar "yawm" module (~/.local/bin/wangan-yawm).
hl.window_rule({
    name     = "wangan-yawm",
    match    = { class = "^wangan-yawm$" },
    float    = true,
    size     = "820 600",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

hl.window_rule({
    name     = "wangan-yawm-add",
    match    = { class = "^wangan-yawm-add$" },
    float    = true,
    size     = "720 240",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

local wangan_popups = { "wangan-launcher", "wangan-yawm", "wangan-yawm-add" }

-- Close every popup window except those of class `keep`.
-- hl.get_windows matches `class` exactly (no regex), so pass the plain name.
function wangan_close_popups(keep)
    for _, class in ipairs(wangan_popups) do
        if class ~= keep then
            for _, w in ipairs(hl.get_windows({ class = class })) do
                hl.dispatch(hl.dsp.window.close({ window = "address:" .. w.address }))
            end
        end
    end
end

function wangan_close_launcher()
    wangan_close_popups()
end

-- Close popups as soon as focus moves elsewhere.
hl.on("window.active", function(win)
    wangan_close_popups(win and win.class)
end)
