# va11halla
> Random quotes from VN "[VA-11 HALL-A: Cyberpunk Bartender Action](https://store.steampowered.com/app/447530/)" by [Sukeban Games](https://sukeban.moe/)

- [Examples](#Examples)
- [Main command parameters](#Parameters)
- [Default language](#Default language)
- [va11-list command](#Lists of)

### Examples
- `[p]va11` - random line
- `[p]va11 ru` - random line on Russian
- `[p]va11 script6.txt` - random line from day 6
- `[p]va11 script6.txt 516` - 516 line on day 6
- `[p]va11 Sei` - random line from Sei
- `[p]va11 ru Сай` - random line from Sei on Russian

### Parameters
- Language (`en`, `ru` if they are in whitelist)
- Script (all scripts: `[p]va11-list scripts 1|2`)
  - Script line
- Character (on needed language)
  - Script to choose line from

### Default Language
You can change your main language (to Russian, for example) on server using:

`[p]va11-config me lang ru`

Also, if you are server admin, you can choose what languages available:
- `[p]va11-config guild whitelist clear` - to clear whitelist
- `[p]va11-config guild whitelist en` - add English to whitelist or remove

You can check all guild settings with `[p]va11-config guild show`

### Lists of
`[p]va11-list characters` - List all characters (except Cameo Dogs)
`[p]va11-list scripts 2` - Second page of scripts (days) list
`[p]va11-list langs` - List available languages on server