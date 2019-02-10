import tornado.ioloop
import tornado.web
import json

global CACHE_PARTS
CACHE_PARTS = {}

class CachesHandler(tornado.web.RequestHandler):

  def get(self, cache_id, part_id):
    if part_id in CACHE_PARTS.get(cache_id, []):
        self.set_status(200)
        return
    self.set_status(404)

  def post(self, cache_id, part_id):
    cache = CACHE_PARTS.setdefault(cache_id, [])
    if part_id in cache:
      self.set_status(409)
      return
    cache.append(part_id)
    self.set_status(200)
    return

  def delete(self, cache_id):
    del CACHE_PARTS[cache_id]
    self.set_status(200)
    return

class StatusHandler(tornado.web.RequestHandler):
  def get(self):
    self.write(json.dumps(CACHE_PARTS))
    self.set_status(200)
    return

def make_app():
  return tornado.web.Application([
    (r"/status/?", StatusHandler),
    (r"/caches/(.*)/parts/(.*)/?", CachesHandler),
  ])

if __name__ == "__main__":
  app = make_app()
  app.listen(8888)
  tornado.ioloop.IOLoop.current().start()
