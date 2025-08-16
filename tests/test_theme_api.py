import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_theme_defaults_and_update():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Defaults
        resp = await client.get("/api/theme")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) >= {"background_color", "text_color", "font_type"}
        assert data["background_color"].lower() == "#ffffff"
        assert data["text_color"].lower() == "#111111"
        assert data["font_type"] == "system"

        # Partial update
        upd = await client.post("/api/theme", json={"background_color": "#000000"})
        assert upd.status_code == 200
        body = upd.json()
        assert body["background_color"].lower() == "#000000"
        # Read back
        again = await client.get("/api/theme")
        assert again.status_code == 200
        after = again.json()
        assert after["background_color"].lower() == "#000000"


@pytest.mark.asyncio
async def test_session_theme_overrides_merge_and_persist():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/api/sessions", json={"name": "S-theme"})
        assert create.status_code == 201
        session_id = create.json()["id"]

        # Set global theme
        await client.post("/api/theme", json={
            "background_color": "#eeeeee",
            "text_color": "#222222",
            "font_type": "arial",
        })

        # Initially effective == global, overrides empty
        g0 = await client.get(f"/api/theme/session/{session_id}")
        assert g0.status_code == 200
        body0 = g0.json()
        assert body0["session_id"] == session_id
        eff0 = body0["effective"]
        assert eff0["background_color"].lower() == "#eeeeee"
        assert eff0["text_color"].lower() == "#222222"
        assert eff0["font_type"] == "arial"
        assert body0["overrides"] == {}

        # Override text_color only for this session
        set_over = await client.put(
            f"/api/theme/session/{session_id}",
            json={"text_color": "#ff0000"},
        )
        assert set_over.status_code == 200
        assert set_over.json()["overrides"] == {"text_color": "#ff0000"}

        g1 = await client.get(f"/api/theme/session/{session_id}")
        eff1 = g1.json()["effective"]
        assert eff1["background_color"].lower() == "#eeeeee"  # from global
        assert eff1["text_color"].lower() == "#ff0000"        # overridden
        assert eff1["font_type"] == "arial"                    # from global


@pytest.mark.asyncio
async def test_theme_presets_save_list_and_apply_builtin_and_custom():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Save a custom preset
        save = await client.post(
            "/api/theme/presets",
            json={
                "name": "solarized",
                "background_color": "#fdf6e3",
                "text_color": "#586e75",
                "font_type": "fira_code",
            },
        )
        assert save.status_code == 200
        # List presets
        lst = await client.get("/api/theme/presets")
        assert lst.status_code == 200
        presets = lst.json()
        assert "built_in" in presets and "custom" in presets
        assert any(p["name"] == "solarized" for p in presets["custom"])  # custom present

        # Apply custom preset
        apply_custom = await client.put("/api/theme", json={"preset": "solarized"})
        assert apply_custom.status_code == 200
        after_custom = apply_custom.json()
        assert after_custom["background_color"].lower() == "#fdf6e3"
        assert after_custom["text_color"].lower() == "#586e75"
        assert after_custom["font_type"] == "fira_code"

        # Apply built-in dark
        apply_dark = await client.put("/api/theme", json={"preset": "dark"})
        assert apply_dark.status_code == 200
        after_dark = apply_dark.json()
        assert after_dark["background_color"].lower() == "#111111"
        assert after_dark["text_color"].lower() == "#f5f5f5"
        assert after_dark["font_type"] == "system"

        # Reset to defaults via light preset
        apply_light = await client.put("/api/theme", json={"preset": "light"})
        assert apply_light.status_code == 200
        after_light = apply_light.json()
        assert after_light["background_color"].lower() == "#ffffff"
        assert after_light["text_color"].lower() == "#111111"
        assert after_light["font_type"] == "system"


@pytest.mark.asyncio
async def test_theme_session_can_apply_preset_and_reject_invalid_colors_and_fonts():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/api/sessions", json={"name": "S2"})
        session_id = create.json()["id"]
        # Save custom preset
        await client.post("/api/theme/presets", json={
            "name": "mydark",
            "background_color": "#000000",
            "text_color": "#eeeeee",
            "font_type": "arial",
        })
        # Apply preset to session
        setp = await client.put(f"/api/theme/session/{session_id}", json={"preset": "mydark"})
        assert setp.status_code == 200
        g = await client.get(f"/api/theme/session/{session_id}")
        eff = g.json()["effective"]
        assert eff["background_color"].lower() == "#000000"
        assert eff["text_color"].lower() == "#eeeeee"
        assert eff["font_type"] == "arial"
        # Try invalid updates (ignored)
        await client.put(f"/api/theme/session/{session_id}", json={"background_color": "red", "font_type": "fantasy"})
        g2 = await client.get(f"/api/theme/session/{session_id}")
        eff2 = g2.json()["effective"]
        # Remains from preset
        assert eff2["background_color"].lower() == "#000000"
        assert eff2["font_type"] == "arial"


