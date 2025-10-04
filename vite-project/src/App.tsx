// src/App.tsx
import React, { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import "./index.css"; // ensure this exists and sets full-height (or use tailwind)

// Put your SAR XYZ tile URL here (replace). For quick test set it to OSM as shown in comments.
const SAR_TILE_URL = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png";
// const SAR_TILE_URL = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"; // useful test URL

export default function App() {
  const mapEl = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null); // use `any` to avoid needing Map types
  const [opacity, setOpacity] = useState(0.75);
  const [visible, setVisible] = useState(true);
  const [log, setLog] = useState<string>("");

  useEffect(() => {
    // quick WebGL availability check
    const canvas = document.createElement("canvas");
    const gl =
      canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) {
      setLog(
        "WebGL not available. Try Chrome/Firefox with hardware acceleration enabled."
      );
      if (mapEl.current)
        mapEl.current.innerHTML =
          "<div style='padding:1rem;color:#900'>WebGL not available</div>";
      return;
    }

    if (!mapEl.current) {
      setLog("Map container not ready");
      return;
    }

    // Create MapLibre map (no heavy typing)
    const map = new (maplibregl as any).Map({
      container: mapEl.current,
      style: {
        version: 8,
        sources: {
          // base raster (OpenStreetMap)
          base: {
            type: "raster",
            tiles: ["https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
          },
        },
        layers: [
          {
            id: "base",
            type: "raster",
            source: "base",
          },
        ],
      },
      center: [0, 0],
      zoom: 2,
    });

    mapRef.current = map;
    setLog((s) => s + "\nMap constructed, waiting for load...");

    map.on("load", () => {
      setLog((s) => s + "\nMap loaded");
      // nav controls
      map.addControl(
        new (maplibregl as any).NavigationControl({ showCompass: true }),
        "top-right"
      );

      // add SAR source/layer (will request tiles from SAR_TILE_URL)
      try {
        if (!map.getSource("sar-tiles")) {
          map.addSource("sar-tiles", {
            type: "raster",
            tiles: [SAR_TILE_URL],
            tileSize: 256,
          });
          map.addLayer({
            id: "sar-layer",
            type: "raster",
            source: "sar-tiles",
            paint: { "raster-opacity": opacity },
          });
          setLog((s) => s + `\nAdded SAR layer (tiles from ${SAR_TILE_URL})`);
        }
      } catch (err) {
        setLog((s) => s + `\nFailed to add SAR layer: ${String(err)}`);
      }

      map.on("click", (e: any) => {
        const { lng, lat } = e.lngLat;
        new (maplibregl as any).Popup()
          .setLngLat([lng, lat])
          .setHTML(
            `<b>Lng:</b> ${lng.toFixed(4)} <br/><b>Lat:</b> ${lat.toFixed(4)}`
          )
          .addTo(map);
      });
    });

    map.on("error", (e: any) => {
      setLog(
        (s) =>
          s +
          `\nMap error: ${JSON.stringify(
            e && e.error ? e.error.message || e.error : e
          )}`
      );
    });

    // force a resize after mount in case layout changed
    setTimeout(() => {
      try {
        map.resize();
      } catch (_) {}
    }, 250);

    return () => {
      try {
        map.remove();
      } catch (_) {}
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // update opacity when changed
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    try {
      if (map.getLayer && map.getLayer("sar-layer")) {
        map.setPaintProperty("sar-layer", "raster-opacity", opacity);
        setLog((s) => s + `\nSet SAR opacity to ${opacity}`);
      }
    } catch (err) {
      setLog((s) => s + `\nFailed to set opacity: ${String(err)}`);
    }
  }, [opacity]);

  // toggle visibility
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    try {
      if (map.getLayer && map.getLayer("sar-layer")) {
        map.setLayoutProperty(
          "sar-layer",
          "visibility",
          visible ? "visible" : "none"
        );
        setLog((s) => s + `\nSAR visibility ${visible}`);
      }
    } catch (err) {
      setLog((s) => s + `\nFailed to toggle visibility: ${String(err)}`);
    }
  }, [visible]);

  return (
    <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
      <div
        ref={mapEl}
        style={{ position: "absolute", inset: 0, background: "#ddd" }}
      />
      <div
        style={{
          position: "absolute",
          left: 12,
          top: 12,
          background: "rgba(255,255,255,0.9)",
          padding: 12,
          borderRadius: 8,
          zIndex: 50,
        }}
      >
        <div style={{ fontWeight: 700, marginBottom: 6 }}>SAR Overlay</div>
        <label
          style={{
            display: "flex",
            gap: 8,
            alignItems: "center",
            marginBottom: 8,
          }}
        >
          <input
            type="checkbox"
            checked={visible}
            onChange={(e) => setVisible(e.target.checked)}
          />
          Visible
        </label>
        <div style={{ marginBottom: 6 }}>
          <label style={{ fontSize: 12 }}>
            Opacity: {Math.round(opacity * 100)}%
          </label>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={opacity}
            onChange={(e) => setOpacity(Number(e.target.value))}
          />
        </div>
        <div style={{ fontSize: 11, color: "#444", marginTop: 6 }}>
          {log
            .split("\n")
            .slice(-6)
            .map((l, i) => (
              <div key={i}>{l}</div>
            ))}
        </div>
      </div>
    </div>
  );
}
