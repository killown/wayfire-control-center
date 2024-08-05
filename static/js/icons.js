const iconClasses = {
  alpha: "fa-alpha",
  animate: "fa-film",
  annotate: "fa-edit",
  autorotate_iio: "fa-sync-alt",
  autostart: "fa-play-circle",
  background_view: "fa-image",
  bench: "fa-bench",
  blur: "fa-tint",
  command: "fa-terminal",
  core: "fa-cogs",
  crosshair: "fa-crosshairs",
  cube: "fa-cube",
  decoration: "fa-border-style",
  expo: "fa-th",
  extra_gestures: "fa-hand-paper",
  output: "fa-desktop",
  input: "fa-keyboard",
  binding: "fa-key",
  scale: "fa-ruler",
  plugin: "fa-plug",
  mouse: "fa-mouse",
  touch: "fa-touch",
  appearance: "fa-paintbrush",
  startup: "fa-play-circle",
  shortcuts: "fa-keyboard",
  theme: "fa-palette",
  layout: "fa-th",
  window: "fa-window-restore",
  workspace: "fa-th-large",
  desktop: "fa-tv",
  default: "fa-cogs",
  compiz: "fa-cube",
  tiling: "fa-th-large",
  expose: "fa-expand",
  wobbly: "fa-arrows-alt",
  zoom: "fa-search-plus",
  fade: "fa-tachometer-alt",
  shadow: "fa-caret-square-right",
  simple_tile: "fa-th-large",
  view_shot: "fa-camera",
  workarounds: "fa-tools",
  wsets: "fa-th",
  vswitch: "fa-exchange-alt",
  switcher: "fa-window-restore",
  water: "fa-tint",
  wm_actions: "fa-tachometer-alt",
  winzoom: "fa-search-plus",
  resize: "fa-arrows-alt",
  preserve_output: "fa-tv",
  vswipe: "fa-arrows-alt",
  wayfire_shell: "fa-terminal",
  wrot: "fa-rotate",
  pixdecor: "fa-paintbrush",
  obs: "fa-video",
  oswitch: "fa-sync",
  move: "fa-arrows",
  mag: "fa-search",
  keycolor: "fa-palette",
  xdg_activation: "fa-cogs",
  ipc: "fa-plug",
  ipc_rules: "fa-rules",
  join_views: "fa-object-group",
  invert: "fa-adjust",
  hinge: "fa-hands",
  grid: "fa-th",
  gtk_shell: "fa-terminal",
  hide_cursor: "fa-eye-slash",
  ghost: "fa-ghost",
  foreign_toplevel: "fa-external-link-alt",
  force_fullscreen: "fa-expand-arrows-alt",
  showrepaint: "fa-redo",
  idle: "fa-pause",
  follow_focus: "fa-crosshairs",
  focus_steal_prevent: "fa-lock",
  focus_change: "fa-bullseye",
  fast_switcher: "fa-fast-forward",
  filters: "fa-filter",
  fisheye: "fa-eye",
  edges: "fa-draw-polygon",
  brightness: "fa-sun",
  always_top: "fa-arrow-up",
  dnd: "fa-hand-paper",
  shadows: "fa-adjust",
  mode: "fa-adjust",
  edge_snap: "fa-expand",
  key: "fa-keyboard",
  view: "fa-eye",
  show: "fa-eye",
  float: "fa-window-restore",
  full: "fa-expand",
  focus: "fa-crosshairs",
  delay: "fa-clock",
  dock: "fa-cogs",
  drag: "fa-arrows",
  drop: "fa-arrow-down",
  bar: "fa-bars",
};

function getIconClass(section) {
  const normalizedSection = section.toLowerCase().replace(/[-_]/g, "_");
  return iconClasses[normalizedSection] || "fa-cogs"; // default icon
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".section-card").forEach((card) => {
    const section = card.dataset.section;
    const iconElement = card.querySelector(".card-icon");
    if (iconElement) {
      iconElement.classList.add(getIconClass(section));
    }
  });
});
