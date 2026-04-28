import os
import requests
import mimetypes
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor


class WPRestAPIException(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        try:
            return f"{self.response.json()}"
        except Exception:
            return f"{self.response.text[:200]}"


class Connect:
    def __init__(self, site_url, username, app_password):
        self.site_url = f'{site_url.strip("/")}/wp-json'
        self.auth = (username, app_password)

        # authentication
        response = requests.get(f"{self.site_url}/wp/v2/users/me", auth=self.auth)
        if response.status_code not in [200, 201]:
            raise WPRestAPIException(response)

        # initialize modules
        self.user = User(self.site_url, self.auth)
        self.page = Page(self.site_url, self.auth)
        self.post = Post(self.site_url, self.auth)
        self.tag = Tag(self.site_url, self.auth)
        self.category = Category(self.site_url, self.auth)
        self.media = Media(self.site_url, self.auth)
        self.comment = Comment(self.site_url, self.auth)


class BaseRequest:
    def __init__(self, site_url, auth):
        self.site_url = site_url
        self.auth = auth

    def request(self, endpoint, method='GET', fields=None, json=None, data=None, files=None, headers=None):
        url = f"{self.site_url}{endpoint}"
        params = {"_fields": fields} if fields else None

        response = requests.request(
            method, url, auth=self.auth, json=json, data=data, params=params, files=files, headers=headers
        )
        if response.status_code in [200, 201, 207]:
            return response

        raise WPRestAPIException(response)


class User(BaseRequest):
    def fetch_all(self, fields=None, **kwargs):
        """
        Get all users.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request("/wp/v2/users", fields=fields, json=kwargs)

    def fetch_one(self, id, fields=None, **kwargs):
        """
        Get a user by ID.
        :param id: User ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/users/{id}", fields=fields, json=kwargs)

    def create(self, username, password, email, fields=None, **kwargs):
        """
        Create a new user.
        :param username: Username.
        :param password: Password.
        :param email: Email.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "username": username,
            "password": password,
            "email": email,
            **kwargs
        }
        return self.request("/wp/v2/users", method="POST", fields=fields, json=data)

    def create_batch(self, users, fields=None):
        """
        Create multiple users in batch.
        :param users: List of user dictionaries.
        :return: Response object.
        """
        user_endpoint = "/wp/v2/users"
        batch_endpoint = "/batch/v1"
        items = [{'method': 'POST', 'path': user_endpoint, 'body': user} for user in users]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def update(self, id, fields=None, **kwargs):
        """
        Update a user by ID.
        :param id: User ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/users/{id}", method="POST", fields=fields, json=kwargs)

    def update_batch(self, users, fields=None):
        """
        Update multiple users in batch.
        :param users: List of user dictionaries.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        user_endpoint = "/wp/v2/users"
        batch_endpoint = "/batch/v1"
        items = [{'method': 'POST', 'path': f"{user_endpoint}/{user['id']}", 'body': user['data']} for user in users]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def delete(self, id, fields=None, force=True, reassign=1):
        """
        Delete a user by ID.
        :param id: User ID.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force delete the user.
        :param reassign: ID to reassign user posts to.
        :return: Response object.
        """
        data = {
            "reassign": reassign,
            "force": force
        }
        return self.request(f"/wp/v2/users/{id}", method="DELETE", fields=fields, json=data)

    def delete_batch(self, ids, fields=None, force=True, reassign=1):
        """
        Delete multiple users by ID.
        :param ids: List of user IDs.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force delete the users.
        :param reassign: ID to reassign user posts to.
        :return: Response object.
        """
        user_endpoint = f"/wp/v2/users"
        items = [{'method': 'DELETE', 'path': f"{user_endpoint}/{id}", 'body': {'reassign': reassign, 'force': force}} for id in ids]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})


class Post(BaseRequest):

    def fetch_all(self, fields=None, post_type="posts", **kwargs):
        endpoint = f"/wp/v2/{post_type}"
        return self.request(endpoint, fields=fields, json=kwargs)

    def create(self, title=None, content=None, fields=None, status="draft", post_type="posts", acf_data=None, **kwargs):
        """
        Create a new post.
        :param title: Post title.
        :param content: Post content.
        :param fields: Comma-separated list of fields to return.
        :param status: Post status.
        :param post_type: Post type.
        :param acf_data: Post data.

        :return: Response object.
        """
        endpoint = f"/wp/v2/{post_type}"
        data = {
            "title": title,
            "content": content,
            "status": status,
            "acf": acf_data,
            **kwargs
        }
        return self.request(endpoint, method="POST", fields=fields, json=data)

    def create_batch(self, posts, fields=None, post_type="posts"):
        post_endpoint = f"/wp/v2/{post_type}"
        items = [{'method': 'POST', 'path': post_endpoint, 'body': post} for post in posts]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def fetch_one(self, id, fields=None, post_type="posts", **kwargs):
        endpoint = f"/wp/v2/{post_type}/{id}"
        return self.request(endpoint, fields=fields, json=kwargs)

    def update(self, id, title=None, content=None, fields=None, post_type="posts", acf_data=None, **kwargs):
        """
        Update a post by ID.
        :param id: Post ID.
        :param fields: Comma-separated list of fields to return.
        :param post_type: Post type.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "title": title,
            "content": content,
            "acf": acf_data,
            **kwargs
        }

        return self.request(f"/wp/v2/{post_type}/{id}", method="POST", fields=fields, json=data)

    def update_batch(self, posts, fields=None, post_type="posts"):
        """
        Update multiple posts in batch.
        :param posts: List of post dictionaries.
        :param fields: Comma-separated list of fields to return.
        :param post_type: Post type.
        :return: Response object.
        """
        items = [{'method': 'POST',
                  'path': f"/wp/v2/{post_type}/{post.get('id')}",
                  'body': post.get('data', {})}
                 for post in posts]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def delete(self, id, fields=None, post_type="posts", force=False):
        """
        Delete a post by ID.
        :param id: Post ID.
        :param fields: Comma-separated list of fields to return.
        :param post_type: Post type.
        :param force: Whether to force delete the post.
        :return: Response object.
        """
        return self.request(f"/wp/v2/{post_type}/{id}", method="DELETE", fields=fields, json={"force": force})

    def delete_batch(self, ids, fields=None, post_type="posts", force=False):
        """
        Delete multiple posts by ID.
        :param ids: List of post IDs.
        :param fields: Comma-separated list of fields to return.
        :param post_type: Post type.
        :return: Response object.
        """
        post_endpoint = f"/wp/v2/{post_type}"
        items = [{'method': 'DELETE', 'path': f"{post_endpoint}/{id}", 'body': {'force': force}} for id in ids]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})


class Page(BaseRequest):
    def fetch_all(self, fields=None, **kwargs):
        """
        Get all pages.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request("/wp/v2/pages", fields=fields, json=kwargs)

    def fetch_one(self, id, fields=None, **kwargs):
        """
        Get a page by ID.
        :param id: Page ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/pages/{id}", fields=fields, json=kwargs)

    def create(self, title, content, fields=None, status="draft", **kwargs):
        """
        Create a new page.
        :param title: Page title.
        :param content: Page content.
        :param fields: Comma-separated list of fields to return.
        :param status: Page status.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "title": title,
            "content": content,
            "status": status,
            **kwargs
        }
        return self.request("/wp/v2/pages", method="POST", fields=fields, json=data)

    def create_batch(self, pages, fields=None):
        """
        Create multiple pages in batch.
        :param pages: List of page dictionaries.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        page_endpoint = f"/wp/v2/pages"
        batch_endpoint = f"/batch/v1"
        items = [{'method': 'POST', 'path': page_endpoint, 'body': page} for page in pages]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def update(self, id, fields=None, **kwargs):
        """
        Update a page by ID.
        :param id: Page ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/pages/{id}", method="POST", fields=fields, json=kwargs)

    def update_batch(self, pages, fields=None):
        """
        Update multiple pages in batch.
        :param pages: List of page dictionaries.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        page_endpoint = f"/wp/v2/pages"
        batch_endpoint = f"/batch/v1"
        items = [{'method': 'POST',
                  'path': f"{page_endpoint}/{page.get('id')}",
                  'body': page.get('data', {})}
                 for page in pages]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def delete(self, id, fields=None, force=False):
        """
        Delete a page by ID.
        :param id: Page ID.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        return self.request(f"/wp/v2/pages/{id}", method="DELETE", fields=fields, json={"force": force})

    def delete_batch(self, ids, fields=None, force=False):
        """
        Delete multiple pages by ID.
        :param ids: List of page IDs.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        page_endpoint = f"/wp/v2/pages"
        items = [{'method': 'DELETE', 'path': f"{page_endpoint}/{id}", 'body': {'force': force}} for id in ids]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})


class Category(BaseRequest):
    def fetch_all(self, taxonomy="categories", fields=None, **kwargs):
        """
        Get all categories.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/{taxonomy}", fields=fields, json=kwargs)

    def fetch_one(self, id, taxonomy="categories", fields=None, **kwargs):
        """
        Get a category by ID.
        :param id: Category ID.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/{taxonomy}/{id}", fields=fields, json=kwargs)

    def create(self, name, taxonomy="categories", fields=None, **kwargs):
        """
        Create a new category.
        :param name: Category name.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "name": name,
            **kwargs
        }
        return self.request(f"/wp/v2/{taxonomy}", method="POST", fields=fields, json=data)

    def create_batch(self, categories, taxonomy="categories", fields=None):
        """
        Create multiple categories in batch.
        :param categories: List of category dictionaries.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        category_endpoint = f"/wp/v2/{taxonomy}"
        batch_endpoint = f"/batch/v1"
        items = [{'method': 'POST', 'path': category_endpoint, 'body': category} for category in categories]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def update(self, id, taxonomy="categories", fields=None, **kwargs):
        """
        Update a category.
        :param id: Category ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/{taxonomy}/{id}", method="POST", fields=fields, json=kwargs)

    def update_batch(self, categories, taxonomy="categories", fields=None):
        """
        Update multiple categories in batch.
        :param categories: List of category dictionaries.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        category_endpoint = f"/wp/v2/{taxonomy}"
        batch_endpoint = f"/batch/v1"
        items = [{'method': 'POST',
                  'path': f"{category_endpoint}/{category.get('id')}",
                  'body': category.get('data', {})}
                 for category in categories]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def delete(self, id, taxonomy="categories", fields=None, force=True):
        """
        Delete a category by ID.
        :param id: Category ID.
        :param taxonomy: Taxonomy type.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        return self.request(f"/wp/v2/{taxonomy}/{id}", method="DELETE", fields=fields, json={"force": force})

    def delete_batch(self, ids, taxonomy="categories", fields=None, force=True):
        """
        Delete multiple categories by ID.
        :param ids: List of category IDs.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        category_endpoint = f"/wp/v2/{taxonomy}"
        items = [{'method': 'DELETE', 'path': f"{category_endpoint}/{id}", 'body': {'force': force}} for id in ids]
        batch_endpoint = f"/batch/v1"
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})


class Tag(BaseRequest):
    def fetch_all(self, fields=None, **kwargs):
        """
        Get all tags.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/tags", fields=fields, json=kwargs)

    def fetch_one(self, id, fields=None, **kwargs):
        """
        Get a tag by ID.
        :param id: Tag ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/tags/{id}", fields=fields, json=kwargs)

    def create(self, name, slug=None, fields=None, **kwargs):
        """
        Create a new tag.
        :param name: Tag name.
        :param slug: Tag slug.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "name": name,
            "slug": slug or name,
            **kwargs
        }
        return self.request("/wp/v2/tags", method="POST", fields=fields, json=data)

    def create_batch(self, tags, fields=None):
        """
        Create multiple tags in batch.
        :param tags: List of tag dictionaries.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        tag_endpoint = "/wp/v2/tags"
        batch_endpoint = "/batch/v1"
        items = [{'method': 'POST', 'path': tag_endpoint, 'body': tag} for tag in tags]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def update(self, id, fields=None, **kwargs):
        """
        Update a tag by ID.
        :param id: Tag ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/tags/{id}", method="POST", fields=fields, json=kwargs)

    def update_batch(self, tags, fields=None):
        """
        Update multiple tags in batch.
        :param tags: List of tag dictionaries.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        tag_endpoint = "/wp/v2/tags"
        batch_endpoint = "/batch/v1"
        items = [{'method': 'POST',
                  'path': f"{tag_endpoint}/{tag.get('id')}",
                  'body': tag.get('data', {})}
                 for tag in tags]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})

    def delete(self, id, fields=None, force=True):
        """
        Delete a tag by ID.
        :param id: Tag ID.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        return self.request(f"/wp/v2/tags/{id}", method="DELETE", fields=fields, json={"force": force})

    def delete_batch(self, ids, fields=None, force=True):
        """
        Delete multiple tags by ID.
        :param ids: List of tag IDs.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        tag_endpoint = "/wp/v2/tags"
        batch_endpoint = "/batch/v1"
        items = [{'method': 'DELETE', 'path': f"{tag_endpoint}/{id}", 'body': {'force': force}} for id in ids]
        return self.request(batch_endpoint, method="POST", fields=fields, json={"requests": items})


class Media(BaseRequest):
    def fetch_all(self, fields=None, **kwargs):
        """
        Get all media items.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request("/wp/v2/media", fields=fields, json=kwargs)

    def fetch_one(self, id, fields=None, **kwargs):
        """
        Get a media item by ID.
        :param id: Media item ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/media/{id}", fields=fields, json=kwargs)

    def upload(self, file_path, fields=None, **kwargs):
        """
        Upload a media item.
        :param file_path: Path to the media file.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        file_path = str(file_path)
        filename = os.path.basename(file_path)
        filename = quote(filename, safe='')
        mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, mime)}
                headers = {"Content-Disposition": f"attachment; filename={filename}"}
                response = self.request("/wp/v2/media", method="POST", fields=fields, files=files, data=kwargs, headers=headers)
                return {"status": "success", "file": file_path, "data": response.json()}
        except WPRestAPIException as e:
            return {"status": "error", "file": file_path, "error_msg": str(e)}
        except Exception as e:
            return {"status": "error", "file": file_path, "error_msg": f"System Error: {str(e)}"}

    def upload_batch(self, medias, fields=None, max_workers=5):
        """
        Upload multiple media items in batch.
        :param medias: List of media dictionaries.
            Each dictionary should contain 'file_path' (path to the media file) and 'data' (dictionary of additional data).
        :param max_workers: Maximum number of concurrent uploads.
        :return: List of upload results.

        example:
        medias = [
            {"file_path": file_path_1, "data": {"alt_text": "text 1"}},
            {"file_path": file_path_2, "data": {"alt_text": "text 2"}}
        ]
        results = connect.media.upload_batch(medias)
        print(results)
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for media in medias:
                results.append(executor.submit(self.upload, media.get('file_path'), fields=fields, **media.get('data', {})))

            results = [future.result() for future in results]
            return results

    def update(self, id, fields=None, **kwargs):
        """
        Update a media item by ID.
        :param id: Media item ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/media/{id}", method="POST", fields=fields, data=kwargs)

    def update_batch(self, medias, fields=None, max_workers=5):
        """
        Update multiple media items in batch.
        :param medias: List of media dictionaries.
            Each dictionary should contain 'id' (media item ID) and 'data' (dictionary of additional data).
        :param max_workers: Maximum number of concurrent updates.
        :return: List of update results.

        example:
        medias = [
            {"id": 1, "data": {"alt_text": "text 1"}},
            {"id": 2, "data": {"alt_text": "text 2"}}
        ]
        results = connect.media.update_batch(medias)
        print(results)
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for media in medias:
                results.append(executor.submit(self.update, media.get('id'), fields=fields, **media.get('data', {})))

            results = [future.result().json() for future in results]
            return results

    def delete(self, id, fields=None, force=True):
        """
        Delete a media item by ID.
        :param id: Media item ID.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :return: Response object.
        """
        return self.request(f"/wp/v2/media/{id}", method="DELETE", fields=fields, json={"force": force})

    def delete_batch(self, ids, fields=None, force=True, max_workers=5):
        """
        Delete multiple media items by ID.
        :param ids: List of media item IDs.
        :param fields: Comma-separated list of fields to return.
        :param force: Whether to force deletion.
        :param max_workers: Maximum number of concurrent deletions.
        :return: List of deletion results.
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for id in ids:
                results.append(executor.submit(self.delete, id, fields=fields, force=force))

            results = [future.result().json() for future in results]
            return results


class Comment(BaseRequest):
    def fetch_all(self, fields=None, **kwargs):
        """
        Get all comments.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request("/wp/v2/comments", fields=fields, json=kwargs)

    def fetch_one(self, id, fields=None, **kwargs):
        """
        Get a comment by ID.
        :param id: Comment ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/comments/{id}", fields=fields, json=kwargs)

    def create(self, post, content, fields=None, **kwargs):
        """
        Create a new comment.
        :param post: Post ID.
        :param content: Comment content.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        data = {
            "post": post,
            "content": content,
            **kwargs
        }
        return self.request("/wp/v2/comments", method="POST", fields=fields, json=data)

    def update(self, id, fields=None, **kwargs):
        """
        Update a comment by ID.
        :param id: Comment ID.
        :param fields: Comma-separated list of fields to return.
        :param kwargs: Additional query parameters.
        :return: Response object.
        """
        return self.request(f"/wp/v2/comments/{id}", method="POST", fields=fields, json=kwargs)

    def delete(self, id, fields=None, force=False, **kwargs):
        """
        Delete a comment by ID.
        :param id: Comment ID.
        :param fields: Comma-separated list of fields to return.
        :return: Response object.
        """
        data = {
            "force": force,
            **kwargs
        }
        return self.request(f"/wp/v2/comments/{id}", method="DELETE", fields=fields, json=data)


if __name__ == "__main__":
    pass
