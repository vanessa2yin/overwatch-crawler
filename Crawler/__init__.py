import json
from Crawler.CrawlerUtil import fetch


def main():
    # Initialize Hero List
    hero_list = ["Ana", "Baptiste", "Bastion", "D-va", "Doomfist", "Genji", "Hanzo", "Junkrat", "Lucio", "McCree",
                 "Mei", "Mercy", "Moira", "Orisa", "Pharah", "Reaper", "Reinhardt", "Roadhog", "Soldier-76", "Sombra",
                 "Symmetra", "Torbjorn", "Tracer", "Widowmaker", "Winston", "Zarya", "Zenyatta"]
    all_hero_dict = {}
    print("Crawler starts.")

    # Iterating through heroes
    for hero_name in hero_list:
        single_hero_info = fetch(hero_name)
        print("Successfully fetched: " + hero_name)
        all_hero_dict[hero_name] = single_hero_info

    file_name = 'ow_hero_data.json'
    with open(file_name, 'w+') as fp:
        json.dump(all_hero_dict, fp, indent=2)

    print("Crawler done.")
    print("Result file: " + file_name)


if __name__ == "__main__":
    main()
