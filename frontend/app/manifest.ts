import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SIDEC",
    short_name: "SIDEC",
    description: "Sistema de distribución y consignación",
    start_url: "/",
    display: "standalone",
    background_color: "#f5f7fb",
    theme_color: "#1f7a3d",
  };
}
