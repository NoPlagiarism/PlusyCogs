# exists
> Cog with generators a-like This Does Not Exist.

- [Install](#install)
- [Generators](#list-of-generators)
- [Generators blacklist](#exclude-generators-in-guild-server)
- [Ultra-Disable NSFW](#disable-nsfw-in-nsfw-channels)

### Install
- `[p]repo add plusycogs https://github.com/NoPlagiarism/PlusyCogs`
- `[p]cog install plusycogs exists`


### Example

`[p]exists cat` - cat generator.

### List of generators

- `cat` from [thiscatdoesnotexist.com](https://thiscatdoesnotexist.com)
- `horse` from [thishorsedoesnotexist.com](https://thishorsedoesnotexist.com)
- `person` from [thispersondoesnotexist.com](https://thispersondoesnotexist.com)
- `fursona` from [thisfursonadoesnotexist.com](https://thisfursonadoesnotexist.com)
- `pony` from [thisponydoesnotexist.net](https://thisponydoesnotexist.net)
- `nightsky` from [arthurfindelair.com/thisnightskydoesnotexist](https://arthurfindelair.com/thisnightskydoesnotexist)
- `map` from [thismapdoesnotexist.com](https://thismapdoesnotexist.com)
- `waifu` from [thiswaifudoesnotexist.net](https://thiswaifudoesnotexist.net)
- `beach` from [thisbeachdoesnotexist.com](https://thisbeachdoesnotexist.com)
- `sneaker` from [thissneakerdoesnotexist.com](https://thissneakerdoesnotexist.com)
- `pepe` from [thispepedoesnotexist.co.uk](https://thispepedoesnotexist.co.uk)
- `city` from [thiscitydoesnotexist.com](https://thiscitydoesnotexist.com)
- `eye` from [thiseyedoesnotexist.com](https://thiseyedoesnotexist.com)
- `tits` [NSFW] from [thesetitsdonotexist.com](https://thesetitsdonotexist.com)

### Exclude generators in guild (server)

There 2 ways: [red built-in](https://docs.discord.red/en/stable/cog_guides/core.html#command-disable) and blacklist

`[p]exists-config guild blacklist waifu` - to disable waifu generator

### Disable NSFW in NSFW channels

NSFW generators are enabled in NSFW channels only. But you can disable those generators, even in NSFW channels

`[p]exists-config guild nsfw`

Repeat command to enable again