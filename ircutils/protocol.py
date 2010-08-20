""" This module mainly focuses on the details of the IRC protocol, so it covers
actions such as line parsing and validation.
"""
import re

#TODO: Add in mode parsing support.


name_symbols = {
    "+": "voice",
    "%": "halfop",
    "@": "op",
    "&": "protectedop",
    "~": "owner"
    }


def parse_line(data):
    """ Takes an IRC line and breaks it into the three main parts; the prefix,
    command, and parameters. It gets returned in the form of 
    ``(prefix, command, params)``.
    This follows :rfc:`2812#2.3.1`, section 2.3.1 regarding message format. 
                
        >>> message = ":nickname!myuser@myhost.net PRIVMSG #gerty :Hello!"
        >>> parse_line(message)
        ('nickname!myuser@myhost.net', 'PRIVMSG', ['#gerty', 'Hello!'])
    """
    if data[0] == ":":
        prefix, data = data[1:].split(" ", 1)
    else:
        prefix = None
    if " :" in data:
        data, trailing = data.split(" :", 1)
        params = data.split()
        params.append(trailing)
    else:
        params = data.split()
    return prefix, params[0], params[1:]


def parse_prefix(prefix):
    """ Take the prefix of an IRC message and split it up into its main parts
    as defined by :rfc:`2812#2.3.1`, section 2.3.1 which shows it consisting 
    of a server name or nick name, the user, and the host. This function 
    returns a 3-part tuple in the form of ``(nick, user, host)``. If user 
    and host aren't present in the prefix, they will be equal to ``None``.
        
        >>> message = ":nickname!myuser@myhost.net PRIVMSG #gerty :Hello!"
        >>> prefix, cmd, params = parse_line(message)
        >>> parse_prefix(prefix)
        ('nickname', 'myuser', 'myhost.net')
    """
    if prefix is None:
        return None, None, None
    if "@" in prefix:
        prefix, host = prefix.split("@", 1)
    else:
        host = None
    if "!" in prefix:
        nick, user = prefix.split("!", 1)
    else:
        nick = prefix
        user = None
    return nick, user, host


_special_chars = ('-', '[', ']', '\\', '`', '^', '{', '}', '_')
def is_nick(nick):
    """ Checks to see if a nickname `nick` is valid.
    According to :rfc:`2812#2.3.1`, section 2.3.1, a nickname must start 
    with either a letter or one of the allowed special characters, and after
    that it may consist of any combination of letters, numbers, or allowed 
    special characters.
    """
    if not nick[0].isalpha() and nick[0] not in _special_chars:
        return False
    for char in nick[1:]:
        if not char.isalnum() and char not in _special_chars:
            return False
    return True


def filter_nick(nick):
    """ Removes all of the invalid characters from a nick. """
    nick = filter(lambda ch:ch.isalnum() or ch in _special_chars, iter(nick))
    if len(nick) == 0:
        return None
    return nick


_channel_regex = re.compile("(?i)(?:#|\+|![a-z0-9]{5}|&)[^\x00\x07\s,\:]+$")
def is_channel(channel):
    """ Checks to see if ``channel`` is a valid channel name.
    It doesn't check if the channel exists, rather only whether the name *could*
    be a channel.
        
       >>> is_channel("#ircutils")
       True
       >>> is_channel("#invalid channel")
       False
       >>> is_channel("#also_inv:alid")
       False
    """
    return _channel_regex.match(channel) is not None




class Channel(object):
    def __init__(self):
        self.name = None
        self.user_list = []

    def __repr__(self):
        return "<Channel %s>" % (self.name, self.user_list)


if __name__ == "__main__":
    import doctest
    doctest.testmod()