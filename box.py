import math

class BoxModel:
	def __init__(self, box_min_x, box_max_x, box_min_y, box_max_y):

		self.box = (box_min_x, box_max_x, box_min_y, box_max_y)

		self.reset()
		print "==== BoxModel ====="
		print "Box:", self.box
		print "Ball:", self.ball
		print "Pad:", self.pad
		print "Bricks", self.bricks
		print "==== BoxMode END ====="

	def reset(self):
		(box_min_x, box_max_x, box_min_y, box_max_y) = self.box
		self.pad = int(box_max_x - box_min_x)/2
		self.ball = (self.pad + 0.5, 0.0, 1, 1.0)
		self.bricks = [1 for _ in xrange(box_min_x, box_max_x)]

	def _normalizeVelocity(self):
		x, y, _vx, _vy = self.ball
		# nromalize
		vx = _vx/max(abs(_vx), abs(_vy))
		vy = _vy/max(abs(_vx), abs(_vy))
		# ensure normalized speed
		assert -1 <= vx <= 1, self.ball
		assert -1 <= vy <= 1, self.ball
		self.ball = (x, y, vx, vy)

	def bounce(self):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		self._normalizeVelocity()
		x, y, vx, vy = self.ball
		
		brickHit = False
		# ensure up direction
		assert vy > 0
		# ensure ball starts at bottom
		assert y == 0

		ball = self.ball

		count = 0

		while True:
			x, y, vx, vy = ball
			count = count + 1
			assert count < 100, ball
			assert box_min_x < x < box_max_x, ball
			assert box_min_y <= y <= box_max_y, ball

			if vx < 0:
				newy = vy/vx * (box_min_x - x) + y
				# assert (box_min_x - x) != 0
				if box_min_y < newy < box_max_y:
					ball = (box_min_x+0.01, newy, -vx, vy)
					# print "hit left", ball
				elif newy >= box_max_y:
					k = vy/vx
					x = (box_max_y - y) / k + x
					ball = (x+0.01, box_max_y, vx, -vy)
					# print "hit top", ball
					brickHit, self.checkBrickHit(ball)
				elif newy <= box_min_y:
					k = vy/vx
					x = (box_min_y - y) / k + x
					ball = (x+0.01, box_min_y, vx, -vy)
					# print "hit bottom", ball
					break

			if vx > 0:
				newy = vy/vx * (box_max_x - x) + y
				# assert (box_max_x - x) != 0
				if box_min_y < newy < box_max_y:
					ball = (box_max_x-0.01, newy, -vx, vy)
					# print "hit right", ball
				elif newy >= box_max_y:
					k = vy/vx
					x = (box_max_y - y) / k + x
					ball = (x-0.01, box_max_y, vx, -vy)
					# print "hit top", ball
					brickHit = self.checkBrickHit(ball)
				elif newy <= box_min_y:
					k = vy/vx
					x = (box_min_y - y) / k + x
					ball = (x-0.01, box_min_y, vx, -vy)
					# print "hit bottom", ball
					break

			if vx == 0:
				brickHit = self.checkBrickHit(ball)
				ball = (x, y, vx, vy)
				break

		# set ball position
		self.ball = ball
		self._normalizeVelocity()

		x, y, vx, vy = self.ball
		# ensure we ended up at bottom
		assert y == box_min_y, y
		return brickHit

	def checkBrickHit(self, ball):
		box_min_x, box_max_x, box_min_y, box_max_y = self.box
		x, y, _, _ = ball

		assert y == box_max_y or y == box_min_x

		idx = int(x - box_min_x)
		idx = min(idx, len(self.bricks)-1)

		assert -1 < idx < len(self.bricks), ball

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
	
	bm = BoxModel(0, 10, 0, 10)

	for i in xrange(50):
		b = bm.bounce()
		x, _, _, _ = b
		bm.movePad(int(x))
		print "===== %d =====" % i
		print b
		print bm.bricks
		print bm.pad
		assert bm.checkPad() is True
		if sum(bm.bricks) == 0:
			print "You won in %dth try" % i
			break

