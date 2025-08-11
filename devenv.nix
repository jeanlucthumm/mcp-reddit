{pkgs, ...}: {
  packages = with pkgs; [
    ruff
    pyright
  ];

  dotenv.enable = true;

  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
    venv.enable = true;
  };

  processes = {};

  tasks = {};
}
