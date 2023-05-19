from pathlib import Path
from random  import randint

from rubika.fileIO import uploadFile
from rubika.configs import makeRubinoData, welcome, __version__, __license__, __copyright__

class Rubino:
    def __init__(self, auth:str):
        self.auth = auth
        self.profileID = [i['id'] for i in self.getProfileList().get("data").get("profiles") if i['is_default']][0]
        welcome(f"rubika library version {__version__}\n{__copyright__}\n→ docs : https://rubikalib.github.io\n\nswitching rubino...")

    def addPost(self, file:str, caption:str=None, isMultiFile:bool=None, postType:str="Picture"):
        uresponse:list = self.fileUpload(file, Type=postType)
        return makeRubinoData(self.auth, "addPost", {"caption": caption, "file_id": uresponse[0]['file_id'], "hash_file_receive": uresponse[1], "height": "800", "width": "800", "is_multi_file": isMultiFile, "post_type": postType, "rnd": randint(100000, 999999999), "thumbnail_file_id": uresponse[0]['file_id'], "thumbnail_hash_file_receive": uresponse[1], "profile_id": self.profileID})

    def addStory(self, duration, width, height, storyType="Picture"):
        uresponse:list = self.fileUpload(file, Type=storyType)
        return makeRubinoData(self.auth, "addStory", {"duration": duration, "file_id": uresponse[0]['file_id'], "hash_file_receive": uresponse[1], "height": height, "profile_id": self.profileID, "rnd": randint(100000, 999999999), "story_type": storyType, "thumbnail_file_id": uresponse[0]['file_id'], "thumbnail_hash_file_receive": uresponse[1], "width": width})

    bookmark          = lambda self, postID, postProfileID       : makeRubinoData(self.auth, "postBookmarkAction", {"action_type": "Bookmark","post_id": postID,"post_profile_id": postProfileID,"profile_id": self.profileID})

    createPage        = lambda self, name, username, bio=None    : makeRubinoData(self.auth, "createPage", {"bio": bio,"name": name,"username": username})
    comment           = lambda self, text, postID, postProfileID : makeRubinoData(self.auth, "addComment", {"content": text,"post_id": postID, "post_profile_id": postProfileID, "rnd": str(randint(100000,999999999)) ,"profile_id": self.profileID})

    fileUpload        = lambda self, file, Type="Picture": uploadFile(self, file, rubino=True, rubinoFType=Type, rubinoFRequest=self.requestUploadFile)
    follow            = lambda self, followee_id: makeRubinoData(self.auth, "requestFollow", {"f_type": "Follow", "followee_id": followee_id, "profile_id": self.profileID})
    
    getComments        = lambda self, postID, postProfileID, limit=50, sort="FromMax" : makeRubinoData(self.auth, "getComments", {"equal": False, "limit": limit, "sort": sort, "post_id": postID, "profile_id": self.profileID, "post_profile_id": postProfileID})
    getMyProfileInfo   = lambda self                                                  : makeRubinoData(self.auth, "getMyProfileInfo", {"profile_id": self.profileID})
    getPostByShareLink = lambda self, shareString                                     : makeRubinoData(self.auth, "getPostByShareLink", {"share_string": shareString.replace('https://rubika.ir/post/', ''), "profile_id": self.profileID})
    getProfileList     = lambda self, equal=False, limit=10, sort="FromMax"           : makeRubinoData(self.auth, "getProfileList", {"equal": equal,"limit": limit,"sort": sort})
    getProfilePosts    = lambda self, targetProfileID, limit=51, sort="FromMax"       : makeRubinoData(self.auth, "getProfilePosts", {"equal": False, "limit": limit, "sort": sort, "target_profile_id": targetProfileID, "profile_id": self.profileID})
    getRecentPosts     = lambda self, equal=False, limit=30, sort="FromMax"           : makeRubinoData(self.auth, "getRecentFollowingPosts", {"equal": equal, "limit": limit, "sort": sort, "profile_id": self.profileID})
    getShareLink       = lambda self, postID, postProfileID                           : makeRubinoData(self.auth, "getShareLink", {"post_id": postID, "post_profile_id": postProfileID, "profile_id": self.profileID})
    getStories         = lambda self, targetProfileID, limit=100                      : makeRubinoData(self.auth, "getProfileStories", {"limit": limit, "profile_id": targetProfileID})
    getStoryIds        = lambda self, targetProfileID                                 : makeRubinoData(self.auth, "getStoryIds", {"profile_id": self.profileID, "target_profile_id": targetProfileID})

    isExist           = lambda self, username: makeRubinoData(self.auth, "isExistUsername", {"username": username.replace('@','')})

    like              = lambda self, post_id, post_profile_id: makeRubinoData(self.auth, "likePostAction", {"action_type": "Like", "post_id": post_id, "post_profile_id": post_profile_id, "profile_id": self.profileID})

    reloadProfile     = lambda self                                  : makeRubinoData(self.auth, "updateProfile", {"profile_id": self.profileID, "profile_status": "Public"})
    requestUploadFile = lambda self, file, size=None, Type="Picture" : makeRubinoData(self.auth, "requestUploadFile", {"file_name": file.split("/")[-1], "file_size": size or Path(file).stat().st_size, "file_type": Type, "profile_id": self.profileID})

    unbookmark        = lambda self, postID, postProfileID : makeRubinoData(self.auth, "postBookmarkAction", {"action_type": "Unbookmark","post_id": postID,"post_profile_id": postProfileID,"profile_id": self.profileID})
    unfollow          = lambda self, followee_id: makeRubinoData(self.auth, "requestFollow", {"f_type": "Unfollow", "followee_id": followee_id, "profile_id": self.profileID})
    unlike            = lambda self, post_id, post_profile_id: makeRubinoData(self.auth, "likePostAction", {"action_type": "Unlike", "post_id": post_id, "post_profile_id": post_profile_id, "profile_id": self.profileID})
    updateProfile     = lambda self, name=None, bio=None, email=None: makeRubinoData(self.auth, "updateProfile", {"name": name, "bio": bio, "email": email})
    
    viewPost          = lambda self, post_id, post_profile_id   : makeRubinoData(self.auth, "addPostViewCount", {"post_id": post_id, "post_profile_id": post_profile_id})
    viewStories         = lambda self, storyIds, storyProfileID : makeRubinoData(self.auth, "addViewStory", {"profile_id": self.profileID, "story_ids": storyIds, "story_profile_id": storyProfileID})