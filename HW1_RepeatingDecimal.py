import math
import re
from decimal import Decimal, getcontext

########################################################
# TODO: MUST REPLACE THIS WITH YOUR STUDENT ID
student_id = "2025150009"  # Replace with your student ID
########################################################

class RepeatingDecimal:
    def __init__(self, sign, int_part, non_repeat, repeat):
        self.__sign = sign
        self.__int_part = int_part
        self.__non_repeat = list(non_repeat)
        self.__repeat = list(repeat)
        self.cleanup()

    @classmethod
    def fromString(cls, s):
        pattern = r'^([+-]?)(\d+)(?:\.(\d*?))?(?:\[(\d+)\])?$'
        match = re.fullmatch(pattern, s.strip())

        sign_str, int_part, non_repeat, repeat = match.groups()

        sign = -1 if sign_str == '-' else 1
        int_part = int(int_part)
        non_repeat = [int(d) for d in (non_repeat or "")]
        repeat = [int(d) for d in (repeat or "")]

        return cls(sign, int_part, non_repeat, repeat)

    @classmethod
    def from_decimal(cls, dec, prec=500):
        getcontext().prec = prec + 10
        s = str(dec)
        sign = 1
        if s.startswith('-'):
            sign = -1
            s = s[1:]
        if 'e' in s or 'E' in s:
            # Handle scientific notation if needed, but for small numbers, unlikely
            dec = dec.quantize(Decimal('1.' + '0' * prec))
            s = str(dec).lstrip('-')
        if '.' not in s:
            return cls(sign, int(s), [], [])
        int_part_str, frac = s.split('.')
        int_part = int(int_part_str) if int_part_str else 0
        # Strip trailing zeros in frac
        frac = frac.rstrip('0')
        if not frac:
            return cls(sign, int_part, [], [])
        non_repeat, repeat = cls.find_repeating(frac)
        obj = cls(sign, int_part, non_repeat, repeat)
        return obj

    @staticmethod
    def find_repeating(frac):
        n = len(frac)
        max_non = min(20, n // 2)
        for non_len in range(max_non + 1):
            tail = frac[non_len:]
            m = len(tail)
            if m == 0:
                return list(map(int, frac[:non_len])), []
            for rep_len in range(1, m // 2 + 1):
                if m % rep_len == 0:
                    rep = tail[:rep_len]
                    if all(tail[i:i + rep_len] == rep for i in range(0, m, rep_len)):
                        return list(map(int, frac[:non_len])), list(map(int, rep))
        # If no repeat, assume terminating
        return list(map(int, frac)), []

    def to_decimal(self, prec=500):
        if self.__sign == 0:
            return Decimal(0)
        getcontext().prec = prec + 10
        s = ''.join(map(str, self.__non_repeat))
        if self.__repeat:
            rep_s = ''.join(map(str, self.__repeat))
            reps_needed = (prec - len(s)) // len(rep_s) + 2
            s += rep_s * reps_needed
        s = str(self.__int_part) + '.' + s[:prec]
        if self.__sign == -1:
            s = '-' + s
        return Decimal(s)

    def cleanup(self):
        if self.__int_part == 0 and not self.__non_repeat and not self.__repeat:
            self.__sign = 0
            return
        carry_from_repeat = self.normalize_repeat()
        if self.__repeat and all(d == 9 for d in self.__repeat):
            carry_from_repeat += 1
            self.__repeat = []
        if self.__repeat and all(d == 0 for d in self.__repeat):
            self.__repeat = []
        carry_from_non_repeat = self.normalize_non_repeat(carry_from_repeat)
        self.__int_part += carry_from_non_repeat
        if self.__int_part < 0:
            if self.__non_repeat or self.__repeat:
                self.__sign = -self.__sign
                self.__int_part = -self.__int_part - 1
                self.__non_repeat = [9 - d for d in self.__non_repeat]
                self.__repeat = [9 - d for d in self.__repeat]
                self.cleanup()
            else:
                self.__sign = -self.__sign
                self.__int_part = -self.__int_part
        if self.__repeat:
            l = len(self.__repeat)
            for k in range(1, l + 1):
                if l % k == 0:
                    prefix = self.__repeat[:k]
                    if prefix * (l // k) == self.__repeat:
                        self.__repeat = prefix
                        break
        if self.__repeat:
            rl = len(self.__repeat)
            while len(self.__non_repeat) >= rl and self.__non_repeat[-rl:] == self.__repeat:
                self.__non_repeat = self.__non_repeat[:-rl]
        if not self.__repeat:
            while self.__non_repeat and self.__non_repeat[-1] == 0:
                self.__non_repeat.pop()
        if self.__int_part == 0 and not self.__non_repeat and not self.__repeat:
            self.__sign = 0

    def normalize_repeat(self):
        if not self.__repeat:
            return 0
        l = len(self.__repeat)
        n = 5
        temp = self.__repeat * n
        carry = 0
        for i in range(len(temp) - 1, -1, -1):
            d = temp[i] + carry
            temp[i] = d % 10
            carry = d // 10
            while temp[i] < 0:
                temp[i] += 10
                carry -= 1
        self.__repeat = temp[:l]
        return carry

    def normalize_non_repeat(self, carry_in):
        if not self.__non_repeat:
            return carry_in
        carry = carry_in
        for i in range(len(self.__non_repeat) - 1, -1, -1):
            d = self.__non_repeat[i] + carry
            self.__non_repeat[i] = d % 10
            carry = d // 10
            while self.__non_repeat[i] < 0:
                self.__non_repeat[i] += 10
                carry -= 1
        return carry

    def __neg__(self):
        return RepeatingDecimal(-self.__sign, self.__int_part, self.__non_repeat, self.__repeat)

    def get_digit(self, pos):
        if pos <= len(self.__non_repeat):
            return self.__non_repeat[pos - 1]
        elif self.__repeat:
            return self.__repeat[(pos - len(self.__non_repeat) - 1) % len(self.__repeat)]
        else:
            return 0

    def __add__(self, other):
        new_int_part = self.__sign * self.__int_part + other.__sign * other.__int_part
        l1 = len(self.__non_repeat)
        l2 = len(other.__non_repeat)
        max_l = max(l1, l2)
        p1 = len(self.__repeat) if self.__repeat else 0
        p2 = len(other.__repeat) if other.__repeat else 0
        lcm = math.lcm(p1, p2) if p1 and p2 else (p1 or p2)
        if p1:
            self_repeat_ext = self.__repeat * (lcm // p1)
        else:
            self_repeat_ext = [0] * lcm
        if p2:
            other_repeat_ext = other.__repeat * (lcm // p2)
        else:
            other_repeat_ext = [0] * lcm
        result_repeat = [self.__sign * self_repeat_ext[j] + other.__sign * other_repeat_ext[j] for j in range(lcm)]
        result_non_repeat = [self.__sign * self.get_digit(j + 1) + other.__sign * other.get_digit(j + 1) for j in range(max_l)]
        new_sign = 1
        new = RepeatingDecimal(new_sign, new_int_part, result_non_repeat, result_repeat)
        return new

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        dec_self = self.to_decimal()
        dec_other = other.to_decimal()
        result = dec_self * dec_other
        return self.from_decimal(result)

    def __truediv__(self, other):
        if other.__sign == 0 and other.__int_part == 0 and not other.__non_repeat and not other.__repeat:
            raise ZeroDivisionError("Division by zero")
        dec_self = self.to_decimal()
        dec_other = other.to_decimal()
        result = dec_self / dec_other
        return self.from_decimal(result)

    def __str__(self):
        if self.__sign == 0:
            return "0"
        s = "-" if self.__sign == -1 else ""
        s += str(self.__int_part)
        if self.__non_repeat or self.__repeat:
            s += "."
            s += "".join(map(str, self.__non_repeat))
            if self.__repeat:
                s += "[" + "".join(map(str, self.__repeat)) + "]"
        return s

if __name__ == "__main__":
    # IF YOU WANT TO TEST YOUR CODE, YOU CAN DO SO HERE
    pass