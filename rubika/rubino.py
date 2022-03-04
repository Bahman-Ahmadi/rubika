from rubika.encryption import encryption
from json import dumps,loads
from random import randint
from requests import post

Client = {
	"app_name": "Main",
	"app_version": "2.9.5",
	"lang_code": "fa",
	"package": "ir.resaneh1.iptv",
	"platform": "Android"
}

class Rubino:
	def __init__(self, auth):
		self.auth = auth
		self.enc = encryption(auth)

	@staticmethod
	def _getURL(): return "https://rubino12.iranlms.ir/"

	def getProfilePosts(self, profileId, targetProfileId, limit=51, sort="FromMax"):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"equal": False,
				"limit": limit,
				"sort": sort,
				"target_profile_id": targetProfileId,
				"profile_id": profileId
			},
			"method": "getProfilePosts"
		}),url=Rubino._getURL()))

	def isExist(self, username):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"username": username
			},
			"method": "isExistUserame"
		}),url=Rubino._getURL()))

	def like(self, post_id, post_profile_id, profile_id):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"action_type": "Like",
				"post_id": post_id,
				"post_profile_id": post_profile_id,
				"profile_id": profile_id
			},
			"method": "likePostAction"
		}),url=Rubino._getURL()))

	def unlike(self, post_id, post_profile_id, profile_id):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"action_type": "Unlike",
				"post_id": post_id,
				"post_profile_id": post_profile_id,
				"profile_id": profile_id
			},
			"method": "likePostAction"
		}),url=Rubino._getURL()))

	def follow(self, followee_id, profile_id):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"f_type": "Follow",
				"followee_id": followee_id,
				"profile_id": profile_id
			},
			"method": "requestFollow"
		}),url=Rubino._getURL()))

	def unfollow(self, followee_id, profile_id):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"f_type": "Unfollow",
				"followee_id": followee_id,
				"profile_id": profile_id
			},
			"method": "requestFollow"
		}),url=Rubino._getURL()))

	def viewPost(self, post_id, post_profile_id):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"post_id": post_id,
				"post_profile_id": post_profile_id,
			},
			"method": "addPostViewCount"
		}),url=Rubino._getURL()))

	def getComments(self, profileId, postId, limit=50, sort="FromMax"):
		return loads(post(json=dumps({
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"equal": False,
				"limit": limit,
				"sort": sort,
				"post_id": post_id,
				"profile_id": profileId,
				"post_profile_id": post_id
			},
			"method": "getComments"
		}),url=Rubino._getURL()))

	def updateProfile(self, name=None, bio=None, email=None):
		updates = []
		if name is not None: updates.append("name")
		if bio is not None: updates.append("bio")
		if email is not None: updates.append("email")

		result = {}
		for i in updates: result[i] = exec(i)

		return post(json={
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": result,
			"method": "updateProfile"
		}, url=Rubino._getURL())

	def requestUploadFile(self, fileName, fileSize:int, fileType, profileId):
		return post(json={
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"file_name": fileName,
				"file_size": fileSize,
				"file_type": fileType,
				"profile_id": profileId
			},
			"method": "requestUploadFile"
		}, url=Rubino._getURL())

	def addStory(self, duration, hashFile, fileID, storyType, thumbnailID, thumbnailHash, profileId, width, height):
		return post(json={
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"duration": duration,
				"file_id": fileID,
				"hash_file_receive": hashFile,
				"height": height,
				"profile_id": profileId,
				"rnd": randint(100000, 999999999),
				"story_type": storyType,
				"thumbnail_file_id": thumbnailID,
				"thumbnail_hash_file_receive": thumbnailHash,
				"width": width
			},
			"method": "addStory"
		}, url=Rubino._getURL())

	def getStories(self, profileId, limit=100);
		return post(json={
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": {
				"limit": limit,
				"profile_id": profileId
			},
			"method": "getProfileStories"
		}, url=Rubino._getURL())

	def addPost(self, **kwargs):
		return post(json={
			"api_version": "0",
			"auth": self.auth,
			"client": Client,
			"data": **kwargs,
			"method": "addPost"
		}, url=Rubino._getURL())