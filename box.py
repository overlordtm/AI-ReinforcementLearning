import math

class BoxModel:
	def __init__(self, box_min_x, box_max_x, box_min_y, box_max_y):

		self.box = (box_min_x, box_max_x, box_min_y, box_max_y)
		self.ball = (box_max_x/2, 0.0, 1.2, 1.0)
		self.pad = box_max_x/2
		self.bricks = [1 for _ in xrange(box_min_x, box_max_x)]

		print "Box:", self.box
		print "Ball:", self.ball
		print "Pad:", self.pad
		print "Bricks", self.bricks
		print "============="

	def bounce(self):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		x, y, vx, vy = self.ball

		# ensure up direction
		assert vy > 0
		# ensure ball starts at bottom
		assert y == 0

		ball = self.ball

		while True:
			x, y, vx, vy = ball
			assert box_min_x <= x <= box_max_x
			assert box_min_y <= y <= box_max_y

			# k = (y - y0) / (x - x0)

			if vx < 0:
				newy = vy/vx * (box_min_x - x) + y
				if box_min_y < newy < box_max_y:
					ball = (box_min_x, newy, -vx, vy)
					# print "hit left", ball
				elif newy >= box_max_y:
					k = vy/vx
					x = (box_max_y - y) / k + x
					ball = (x, box_max_y, vx, -vy)
					# print "hit top", ball
					self.checkBrickHit(ball)
				elif newy <= box_min_y:
					k = vy/vx
					x = (box_min_y - y) / k + x
					ball = (x, box_min_y, vx, -vy)
					# print "hit bottom", ball
					break

			if vx > 0:
				newy = vy/vx * (box_max_x - x) + y
				if box_min_y < newy < box_max_y:
					ball = (box_max_x, newy, -vx, vy)
					# print "hit right", ball
				elif newy >= box_max_y:
					k = vy/vx
					x = (box_max_y - y) / k + x
					ball = (x, box_max_y, vx, -vy)
					# print "hit top", ball
					self.checkBrickHit(ball)
				elif newy <= box_min_y:
					k = vy/vx
					x = (box_min_y - y) / k + x
					ball = (x, box_min_y, vx, -vy)
					# print "hit bottom", ball
					break

			if vx == 0:
				ball = (x, y, vx, vy)
				break

		(x, y, vx, vy) = ball
		assert y == box_min_y
		self.ball = ball
		return ball

	def checkBrickHit(self, ball):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		x, y, _, _ = ball

		assert y == box_max_y

		idx = int(x - box_min_x)

		assert -1 < idx < len(self.bricks)

		if self.bricks[idx] == 1:
			# print "Hit brick", idx
			self.bricks[idx] = 0
			return True
		else:
			return False

	def checkPad(self):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		x, y, _, _ = self.ball

		assert y == box_min_y
		return self.pad <= x <= self.pad + 1

	def movePad(self, newX):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		x, y, vx, vy = self.ball

		c = math.atan(newX - self.pad)

		self.pad = newX
		self.ball = (x, y, vx + c, vy)


if __name__ == "__main__":
	
	bm = BoxModel(0, 13, 0, 12)

	for i in xrange(50):
		b = bm.bounce()
		x, _, _, _ = b
		bm.movePad(int(x))
		print "===== %d =====" % i
		print b
		print bm.bricks
		print "Pad pos: ", bm.pad
		assert bm.checkPad() is True
		if sum(bm.bricks) == 0:
			print "You won in %dth try" % i
			break

