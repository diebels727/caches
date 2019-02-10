import tornado.ioloop
import tornado.web
import http
import json


CACHE_PARTS = dict()


def serializer(value):
  if isinstance(value, set):
    return list(value)
  return value


class Handler(tornado.web.RequestHandler):
  def complete(self, status, message='', data=None):
    if not data:
      data = {}
    self.set_status(status)
    self.write(json.dumps({
      'metadata': {
        'status': status,
        'message': message
      },
      'data': data
    }, indent=2, default=serializer))


class CachesHandler(Handler):

  def get(self, cache_id, part_id):
    if part_id in CACHE_PARTS.get(cache_id, set()):
        self.complete(http.HTTPStatus.OK)
        return
    self.complete(http.HTTPStatus.NOT_FOUND)

  def post(self, cache_id, part_id):
    cache_part = CACHE_PARTS.setdefault(cache_id, set())
    if part_id in cache_part:
      self.complete(http.HTTPStatus.CONFLICT)
      return
    cache_part.update(part_id)
    self.complete(http.HTTPStatus.CREATED)


class CacheHandler(Handler):

  def delete(self, cache_id):
    try:
      del CACHE_PARTS[cache_id]
    except:
      self.complete(http.HTTPStatus.INTERNAL_SERVER_ERROR)
      return
    self.complete(http.HTTPStatus.OK)


class StatusHandler(Handler):

  def get(self):
    global CACHE_PARTS
    self.complete(http.HTTPStatus.OK, data=CACHE_PARTS)

  def delete(self):
    global CACHE_PARTS
    # invalidate the cache
    CACHE_PARTS = dict()
    self.complete(http.HTTPStatus.OK)

def make_app():
  return tornado.web.Application([
    (r"/status/?", StatusHandler),
    (r"/cache/(.*)/?", CacheHandler),
    (r"/caches/(.*)/parts/(.*)/?", CachesHandler),
  ])

if __name__ == "__main__":
  app = make_app()
  app.listen(8888)
  tornado.ioloop.IOLoop.current().start()
