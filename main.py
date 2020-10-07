import argparse
import requests
import urllib
import json
import random


def get_all_video_in_channel(channel_id, api_key):
    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        try:
            inp = urllib.request.urlopen(url).read()
            resp = json.loads(inp.decode('utf-8'))
        except Exception as inst:
            print(inst)
            exit(0)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append((base_video_url + i['id']['videoId'])[32:45])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links


def auth(username, password, server):
    print(username)
    postdata = {'username':username, 'password':password}
    res = requests.post(server, json=postdata)
    print(res.text)
    return res.json()


def send_all_entries(channel_id, api_key, server, authkey, dry_run=False):
    links = get_all_video_in_channel(channel_id, api_key)
    random.shuffle(links)
    failed_entries = []
    for link in links:
        # Print dry run results if no server address
        if not server:
            dry_run = True
            server = '0.0.0.0'
        res_code, postdata = send_entry(
            server, link, dry_run, authkey)
        if res_code != 200 and res_code != 201:  # STATUS CODE not OK
            failed_entries.append([postdata, res_code])
    return failed_entries


def send_entry(server, entry, dry_run, authkey):
    url = server
    postdata = {
        'archiveURL': entry
    }
    if not dry_run:
        #auth_headers = "Authorization: JWT " + authkey['access_token']
        auth_headers = {'Authorization': 'JWT ' + authkey['access_token']}
        res = requests.post(url, json=postdata, headers=auth_headers)
        res_code = res.status_code
        print(res_code, res)
    else:
        print(postdata)
        res_code = 200  # STATUS CODE OK
    return res_code, postdata


def main(argv):
    if argv.dry_run:
        print("\nThis is a dry run. No data will be loaded to server whether "
              "a server_address has been provided or not.\n")
    elif not argv.server_address:
        print("\nWARNING: A server address was not provided in args. "
              "Only printing results locally. Use the -h arg if you don't "
              "know what this means.\n")
    authkey = auth(argv.auth_username, argv.auth_password, argv.auth_api)
    failed_entries = send_all_entries(
        argv.channel_id, argv.api_key, argv.server_address, authkey, argv.dry_run)

    total_failed_entries = len(failed_entries)
    if total_failed_entries > 1:
        print(
            "\nTHERE WERE {} ENTRIES THAT FAILED TO BE PROCESSED.\n".format(
                total_failed_entries))
        print(failed_entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Pull YouTube video links from channel')
    parser.add_argument(
        '--channel[id', '-c', dest='channel_id', required=True,
        help='the channel id')
    parser.add_argument(
        '--dry_run', '-d', dest='dry_run', action='store_true',
        help='performs a dry run locally when provided with a '
        'server_address')
    parser.add_argument(
        '--server', '-s', dest='server_address', required=False,
        help='the server address for the results to be uploaded')
    parser.add_argument(
        '--user', '-u', dest='auth_username', required=True,
        help='the username to log in to the api with')
    parser.add_argument(
        '--pass', '-p', dest='auth_password', required=True,
        help='the password to log in to the api with')
    parser.add_argument(
        '--auth', '-a', dest='auth_api', required=True,
        help='the auth api')
    parser.add_argument(
        '--youtube-api', '-y', dest='api_key', required=True,
        help='the youtube API key')
    args = parser.parse_args()
    main(args)
