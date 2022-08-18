from random  import randint
from pathlib import Path

from rubika.configs import makeRubinoData, welcome, __version__, __license__, __copyright__

class Rubino:
	def __init__(self, username:str, auth:str):
		self.auth, self.profileID = auth, makeRubinoData(auth, "isExistUsername", {"username": username})["data"]["profile"]["id"]
		welcome(f"rubika library version {__version__}\n{__copyright__}\n→ docs : https://rubikalib.github.io\n\nswitching rubino...")

	addPost           = lambda self, caption, fileID, hashFile, thumbnailID, thumbnailHash, width, height, post_type="Picture", is_multi_file=False: makeRubinoData(self.auth, "addPost", {"caption": caption, "file_id": fileID, "hash_file_receive": hashFile, "height": str(height), "width": str(width), "is_multi_file": is_multi_file, "post_type": post_type, "rnd": randint(100000, 999999999), "thumbnail_file_id": thumbnailID, "thumbnail_hash_file_receive": thumbnailHash, "profile_id": self.profileID})
	addStory          = lambda self, duration, hashFile, fileID, storyType, thumbnailID, thumbnailHash, width, height: makeRubinoData(self.auth, "addStory", {"duration": duration, "file_id": fileID, "hash_file_receive": hashFile, "height": height, "profile_id": self.profileID, "rnd": randint(100000, 999999999), "story_type": storyType, "thumbnail_file_id": thumbnailID, "thumbnail_hash_file_receive": thumbnailHash, "width": width})

	follow            = lambda self, followee_id: makeRubinoData(self.auth, "requestFollow", {"f_type": "Follow", "followee_id": followee_id, "profile_id": self.profileID})
	
	getStories         = lambda self, targetProfileID, limit=100                      : makeRubinoData(self.auth, "getProfileStories", {"limit": limit, "profile_id": targetProfileID})
	getProfilePosts    = lambda self, targetProfileID, limit=51, sort="FromMax"       : makeRubinoData(self.auth, "getProfilePosts", {"equal": False, "limit": limit, "sort": sort, "target_profile_id": targetProfileID, "profile_id": self.profileID})
	getRecentPosts     = lambda self, equal=False, limit=30, sort="FromMax"           : makeRubinoData(self.auth, "getRecentFollowingPosts", {"equal": equal, "limit": limit, "sort": sort, "profile_id": self.profileID})
	getComments        = lambda self, postID, postProfileID, limit=50, sort="FromMax" : makeRubinoData(self.auth, "getComments", {"equal": False, "limit": limit, "sort": sort, "post_id": postID, "profile_id": self.profileID, "post_profile_id": postProfileID})
	getPostByShareLink = lambda self, shareString                                     : makeRubinoData(self.auth, "getPostByShareLink", {"share_string": shareString, "profile_id": self.profileID})

	isExist           = lambda self, username: makeRubinoData(self.auth, "isExistUsername", {"username": username.replace('@','')})

	like              = lambda self, post_id, post_profile_id: makeRubinoData(self.auth, "likePostAction", {"action_type": "Like", "post_id": post_id, "post_profile_id": post_profile_id, "profile_id": self.profileID})

	requestUploadFile = lambda self, file, size=None, Type="Picture": makeRubinoData(self.auth, "requestUploadFile", {"file_name": file.split("/")[-1], "file_size": size or Path(file).stat().st_size, "file_type": Type, "profile_id": self.profileID})

	unfollow          = lambda self, followee_id: makeRubinoData(self.auth, "requestFollow", {"f_type": "Unfollow", "followee_id": followee_id, "profile_id": self.profileID})
	unlike            = lambda self, post_id, post_profile_id: makeRubinoData(self.auth, "likePostAction", {"action_type": "Unlike", "post_id": post_id, "post_profile_id": post_profile_id, "profile_id": self.profileID})
	updateProfile     = lambda self, name=None, bio=None, email=None: makeRubinoData(self.auth, "updateProfile", {"name": name, "bio": bio, "email": email})
	
	viewPost          = lambda self, post_id, post_profile_id: makeRubinoData(self.auth, "addPostViewCount", {"post_id": post_id, "post_profile_id": post_profile_id})