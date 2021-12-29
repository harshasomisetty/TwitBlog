import requests
from requests_oauthlib import OAuth1
import numpy as np
import json
from tqdm import tqdm
import time
import csv


class TwitterAPI:
    def __init__(self,
                 username,
                 bearer_token,
                 key=None,
                 secret=None,
                 token=None,
                 token_secret=None):

        self.endpoint2 = 'https://api.twitter.com/2'
        self.endpoint1 = 'https://api.twitter.com/1.1'
        self.bearer = {"Authorization": "Bearer " + bearer_token}
        self.username = username
        try:
            req = requests.get(self.endpoint2 + "/users/by/username/" +
                               username,
                               headers=self.bearer)
            self.id = req.json()["data"]["id"]
        except Exception as e:
            print(req.status_code)
            raise e
        if key and secret and token and token_secret:
            self.oauth = OAuth1(key, secret, token, token_secret)
            self.content = {"Content-type": "application/json"}

    # get info on a specific user
    def user_lookup(self, user, payload=None):
        options = "?"
        url = self.endpoint2 + "/users"
        if payload:
            options += "user.fields=" + ",".join(payload)

        try:
            req = requests.get(url + "/" + user + options, headers=self.bearer)
            if req.status_code == 200:
                return req.json()['data']
            else:
                req2 = requests.get(url + "/by/username/" + user + options,
                                    headers=self.bearer)
                if req2.status_code == 200:
                    return req2.json()['data']
                else:
                    raise ValueError(req2.url)

        except Exception as e:
            raise ValueError(e)

    # method to get userdata for list of user id
    def multiple_user_lookup(self, ids, payload=None):
        if not payload:
            payload = [
                'created_at', 'description', 'entities', 'id', 'name',
                'protected', 'url', 'username', 'verified', 'public_metrics'
            ]

        follows_data = []
        for i in tqdm(range(0, int(len(ids) / 100) + 1)):
            if len(ids[i * 100:i * 100 + 100]) > 0:
                req = requests.get('https://api.twitter.com/2/users' +
                                   '?user.fields=' + ','.join(payload) +
                                   '&ids=' +
                                   ','.join(ids[i * 100:i * 100 + 100]),
                                   headers=self.bearer)
            else:
                break
            if req.status_code != 200:
                return req
            else:
                follows_data[len(follows_data) - 1:len(follows_data) -
                             1] = req.json()["data"]

        # need to filter dicts because of weird withheld field appearing
        return [{key: dic[key] for key in payload} for dic in follows_data]

    def get_following(self, username):  # use both endpoints for rate limit

        follows = self._get_following1(username)
        if isinstance(follows, int):
            return self._get_following2(username)
        else:
            return follows

            # while user_follows == -1:  #check if too many requests
            #     print("Too many requests")

    # for given user, return list of all ids user follows, endpt2
    def _get_following2(self, username):
        user_id = self.user_lookup(username)["id"]
        url = self.endpoint2 + "/users/" + user_id +\
                               "/following?max_results=1000"

        data = []

        req = requests.get(url, headers=self.bearer)

        if req.status_code != 200:
            return req.status_code

        if "data" not in req.json().keys():
            return []
        else:
            data = req.json()["data"]

            while "next_token" in req.json()["meta"]:
                req = requests.get(url + "&pagination_token=" +
                                   req.json()["meta"]["next_token"],
                                   headers=self.bearer)

                if req.status_code != 200:
                    return req.status_code

                data[len(data) - 1:len(data) - 1] = req.json()["data"]

            return [str(i["id"]) for i in data]

    # for given user, return list of all ids user follows, endpt1
    def _get_following1(self, username):
        url = self.endpoint1 + ("/friends/ids.json?" + "&count=5000" +
                                "&screen_name=" + username)

        req = requests.get(url, auth=self.oauth)
        if req.status_code != 200:
            return req.status_code

        if "ids" not in req.json().keys():
            return []
        else:
            data = req.json()["ids"]

            while req.json()["next_cursor"] > -1:
                req = requests.get(url + "&cursor=" +
                                   req.json()["next_cursor_str"],
                                   auth=self.oauth)
                if req.status_code != 200:
                    return req.status_code
                data[len(data) - 1:len(data) - 1] = req.json()["ids"]

            return [str(i) for i in data]

    # TODO edit to get variable number of tweets
    def get_recent_tweets(self,
                          user_name,
                          count=200,
                          exclude_replies="false",
                          include_rts="false"):

        url = self.endpoint1+"/statuses/user_timeline.json?" +\
                             "count=" + str(count) + "&" +\
                             "tweet_mode=extended&" +\
                             "trim_user=true&" +\
                             "exclude_replies=" + exclude_replies + "&" +\
                             "include_rts=" + include_rts + "&" +\
                             "screen_name=" + user_name

        req = requests.get(url, auth=self.oauth)
        try:
            max_id = req.json()[-1]["id"] - 1
        except Exception:
            print(user_name, "Has no tweets")
            return -1
        data = req.json()

        while True:
            try:
                req = requests.get(url + "&max_id=" + str(max_id),
                                   auth=self.oauth)

                max_id = req.json()[-1]["id"] - 1
                data.extend(req.json())
            except Exception:
                break

        return data

    # returns generator of entire user's tweets
    def get_historical_tweets(self,
                              user_name: str,
                              cnt=500,
                              start_date=None,
                              tweet_fields=None):

        if not start_date:  # normally get tweets from earliest history
            user_data = self.user_lookup(user_name, payload=["created_at"])
            start_date = user_data["created_at"]

        if not tweet_fields:  # my default selected payload parameters
            tweet_fields = [
                "created_at", "in_reply_to_user_id", "referenced_tweets",
                "public_metrics"
            ]

        url = self.endpoint2 + ('/tweets/search/all?max_results=' + str(cnt) +
                                '&start_time=' + start_date + '&query=from:' +
                                user_name + '&expansions=author_id' +
                                '&tweet.fields=' + ','.join(tweet_fields) +
                                '&user.fields=username,location')
        req = requests.get(url, headers=self.bearer)
        try:
            # return req
            data = req.json()["data"]
        except Exception as e:
            print(req)
            raise e

        while "next_token" in req.json()["meta"]:
            try:
                req = requests.get(url + "&next_token=" +
                                   req.json()["meta"]["next_token"],
                                   headers=self.bearer)
                print(req)
                data.extend(req.json()["data"])
            except Exception as e:

                raise e

        return data

    # returns all user ids user1 follows that user2 does not
    def get_follow_differences(self, user1, user2):
        return np.setdiff1d(self.get_following1(user1),
                            self.get_following1(user2))

    # follow a specific user
    def follow_user_id(self, user_id):
        try:
            requests.post(self.endpoint2 + "/users/" + self.id + "/following",
                          auth=self.oauth,
                          headers={"Content-type": "application/json"},
                          data=json.dumps({"target_user_id": user_id}))
        except Exception as e:
            return e

    def rate_limits(self):
        return requests.get(self.endpoint1 +
                            "/application/rate_limit_status.json",
                            auth=self.oauth).json()

    # gets latest 20 tweets
    def home_timeline(self,
                      count=200,
                      exclude_replies="true",
                      include_entities="false"):

        url = self.endpoint1 +\
              "/statuses/home_timeline.json?" +\
              "count=" + str(count) + "&" +\
              "tweet_mode=extended&" +\
              "trim_user=true&" +\
              "exclude_replies=" + exclude_replies + "&" +\
              "include_entities=" + include_entities
        return requests.get(url, auth=self.oauth).json()

    # check for valid authorization
    def test_auth(self):
        return requests.get(self.endpoint2 + "/tweets?ids=1228393702244134912",
                            headers=self.bearer).status_code
