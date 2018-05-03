# This is kept seperate from helpers.py because I may make it more
# than it is here at a later point
import discord
import logging
import io
import sys

from .helpers import role_mention_cleanup

log = logging.getLogger('redbot.sinbadcogs.relays.webhook')


async def get_attach(message: discord.Message) -> discord.File:
    max_size = 8 * 1024 * 1024
    _fp = io.BytesIO()
    a = message.attachments[0]
    await a.save(_fp)
    if sys.getsizeof(_fp) > max_size:
        _fp.close()
        del _fp
        raise AttributeError("Bots cant forward attatchments this large")
    return discord.File(_fp, filename=a.filename)


async def hooked_send(dest: discord.TextChannel, msg: discord.Message):
    """
    Forwards a message, [partially] impersonating the author
    """

    try:
        hooks = await dest.webhooks()
        if hooks:
            hook = hooks[0]
        else:
            hook = await dest.create_webhook()
    except discord.Forbidden:
        log.warning('Message not forwarded due to lack of webhook perms')

    content = role_mention_cleanup(msg)

    if msg.attachments:
        try:
            f = await get_attach(msg)
        except AttributeError:
            f = None
            embed = discord.Embed(
                description='Original attachment (above max forwarding size): '
                '[{0.filename}]({0.url})'.format(msg.attachments[0])
            )
        else:
            embed = None
    else:
        f, embed = None, None

    av = msg.author.avatar_url_as(format='png', static_format='png')

    await hook.send(
        content,
        file=f,
        embed=embed,
        username=msg.author, avatar_url=av
    )
