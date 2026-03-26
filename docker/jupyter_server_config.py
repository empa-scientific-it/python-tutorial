# Configuration file for jupyter server.

c = get_config()  # noqa # type: ignore

# Allow serving files/folders beginning with a dot
c.ContentsManager.allow_hidden = True
