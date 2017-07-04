from vk_raid_defender.cli import cli

if __name__ == '__main__':
    cli.main()
else:
    raise ImportError('этот модуль должен использоваться только для запуска программы')
