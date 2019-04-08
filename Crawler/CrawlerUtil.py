from bs4 import BeautifulSoup
import requests
import string

URL = 'https://overwatch.guide/heroes/'


def get_printable_string(input_str):
    """
    eliminate non-printable char in input_str and return the clean output_str
    :param input_str: input string
    :return: output_str: output string with all printable char
    """
    return "".join(filter(lambda char: char in string.printable, input_str))


def fetch_hero_type(soup):
    """
    fetch hero type from the soup
    """
    hero_type_info = soup.find('span', {'style': "font-size: 18px;"})
    hero_type = hero_type_info.text
    return hero_type


def fetch_bio(soup):
    """
    fetch bio_dict info of the hero from soup and return a bio_dict dict and the position of bio_info in soup
    :return: bio_dict: result bio_dict dict, bio_info: the position of bio_info in soup
    """
    bio_dict = {}

    # find bio_dict info of the hero by style first
    bio_info = soup.find('div', {'style': "line-height: 20px;"})

    # if cannot find by style, find again
    if bio_info is None:
        bio_info = soup.find(text='Bio').parent.parent.next_sibling.next_sibling.next.next

    # parse each of its field
    for info in bio_info.children:
        if hasattr(info, 'text') and info.text != "":
            bio_dict[info.text.split(":")[0]] = get_printable_string(info.text.split(":")[1])

    return bio_dict, bio_info


def fetch_basic_stats(soup):
    """
    fetch basic_stats(number of health, armor, shield) from the soup
    :return: health, armor, shield: number of health, armor, shield
    """
    health_info = soup.find('span', {'class': "vc_label_units"})
    health = int(health_info.text)
    armor_info = health_info.find_next('span', {'class': "vc_label_units"})
    armor = int(armor_info.text)
    shield_info = armor_info.find_next('span', {'class': "vc_label_units"})
    shield = int(shield_info.text)

    return health, armor, shield


def get_ability_start_position(bio_info):
    """
    get the start position of the ability_wrapper_box on the website with the position of bio_info
    :param bio_info: the position of bio_info, where is the start point to find the ability_wrapper_box
    :return: the start position of the ability_wrapper_box
    """
    # the first wrapper is not the correct wrapper (it is an empty wrapper on the website)
    start = bio_info.next_sibling
    while (not hasattr(start, 'div')) or start.div is None or start.div['class'][0] != "wpb_wrapper":
        start = start.next_element

    # find again to find the correct wrapper
    start = start.next_element
    while (not hasattr(start, 'div')) or start.div is None or start.div['class'][0] != "wpb_wrapper":
        start = start.next_element

    return start


def process_single_ability_box(abilities_raw_list, single_ability_box):
    """
    Helper for put_abilities_into_list
    Process single ability box fetched from the website
    Split several abilities and append separately if there are many abilities in one single ability box
    If there is only one, append to abilities_raw_list directly
    Also remove the extra space and newlines from the single_ability_box
    :param abilities_raw_list: list of raw abilities, each one has an ability name and detailed attributes
    :param single_ability_box: one ability box fetched from the website
    """
    single_ability_box = single_ability_box.replace("\n\n", "").strip()
    primary_fire = single_ability_box.find("Primary fire")
    second_fire = single_ability_box.find("Secondary fire")
    if primary_fire != -1:
        abilities_raw_list.append(single_ability_box[:primary_fire])
        if second_fire != -1:
            abilities_raw_list.append(single_ability_box[primary_fire:second_fire])
            abilities_raw_list.append(single_ability_box[second_fire:])
        else:
            abilities_raw_list.append(single_ability_box[primary_fire:])
    else:
        abilities_raw_list.append(single_ability_box)


def put_abilities_into_list(abilities_raw_list, start):
    """
    fetch raw abilities from the start position and put them into abilities_raw_list
    :param abilities_raw_list: list to append
    :param start: position to start in soup
    """
    for single_ability_box in start.children:
        if not hasattr(single_ability_box, 'children'):
            continue
        # only get valid text as the ability detailed info
        for each_text in single_ability_box.children:
            if hasattr(each_text, 'text') and each_text.text.strip():
                process_single_ability_box(abilities_raw_list, each_text.text)


def transform_to_abilities_dict(abilities_dict, abilities_raw_list):
    """
    process the abilities_raw_list to be abilities_dict
    :param abilities_dict: result dict
    :param abilities_raw_list: list to process
    """
    for single_ability_data in abilities_raw_list:
        lines_list = single_ability_data.split("\n")
        ability_name = lines_list[0]
        abilities_dict[ability_name] = {}
        for i in range(1, len(lines_list)):
            if not lines_list[i]:
                continue
            each_line_data = lines_list[i].split(":")

            # each_line_data is in the format of [info], should be included in 'description' category
            if len(each_line_data) == 1:
                abilities_dict[ability_name]['description'] = get_printable_string(each_line_data[0])

            # each_line_data is in the format of [attribute, info]
            else:
                first = get_printable_string(each_line_data[0])
                second = get_printable_string(each_line_data[1])
                abilities_dict[ability_name][first] = second


def fetch(hero_name):
    """
    fetch hero data from the website
    :param hero_name: hero to fetch data
    :return: single_hero_dict: result hero dict
    """
    hero_page = requests.get(URL + hero_name).content
    soup = BeautifulSoup(hero_page, "lxml")

    # fetch hero type
    hero_type = fetch_hero_type(soup)

    # fetch bio
    bio_dict, bio_info = fetch_bio(soup)

    # fetch number of health, armor, shield
    health, armor, shield = fetch_basic_stats(soup)

    # get start position of the ability wrapper box
    start = get_ability_start_position(bio_info)

    # get a list of raw ability data
    abilities_raw_list = []
    put_abilities_into_list(abilities_raw_list, start)

    # dict containing each single ability information
    abilities_dict = {}
    transform_to_abilities_dict(abilities_dict, abilities_raw_list)

    # add hero data into single_hero_dict
    single_hero_dict = {"health": health,
                        "armor": armor,
                        "shield": shield,
                        "type": hero_type,
                        "bio": bio_dict,
                        "abilities": abilities_dict}

    return single_hero_dict
