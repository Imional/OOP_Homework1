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
        # 1. 새로운 비반복부와 반복부의 길이를 결정
        new_non_repeat_len = max(len(self.__non_repeat), len(other.__non_repeat))

        # 반복부가 없는 경우 길이를 1로 간주하여 최소공배수를 계산
        self_repeat_len = len(self.__repeat) or 1
        other_repeat_len = len(other.__repeat) or 1
        new_repeat_len = math.lcm(self_repeat_len, other_repeat_len)

        # 2. 정수부를 먼저 더함
        new_int_part = self.__sign * self.__int_part + other.__sign * other.__int_part

        # 3. 비반복부의 각 자릿수를 더함
        # get_digit(pos)는 소수점 아래 pos번째 숫자를 반환
        new_non_repeat = [
            self.__sign * self.get_digit(i) + other.__sign * other.get_digit(i)
            for i in range(1, new_non_repeat_len + 1)
        ]

        # 4. 반복부의 각 자릿수를 더함
        new_repeat = [
            self.__sign * self.get_digit(i) + other.__sign * other.get_digit(i)
            for i in range(new_non_repeat_len + 1, new_non_repeat_len + new_repeat_len + 1)
        ]

        # 5. 계산된 "정리되지 않은" 값들로 새 객체를 생성
        # __init__ 내부의 cleanup() 메서드가 정규화(자리올림 등)를 처리
        return RepeatingDecimal(1, new_int_part, new_non_repeat, new_repeat)

    def __sub__(self, other):
        return self + (-other)

    def to_fraction(self):
        """Converts the RepeatingDecimal object to a (numerator, denominator) pair."""
        if self.__sign == 0:
            return 0, 1

        # 1. 비반복부(non_repeat)를 분수로 변환
        num_non_repeat_str = ''.join(map(str, self.__non_repeat))
        num_non_repeat = int(num_non_repeat_str) if num_non_repeat_str else 0
        den_non_repeat = 10 ** len(self.__non_repeat)

        # 2. 반복부(repeat)를 분수로 변환
        num_repeat_str = ''.join(map(str, self.__repeat))
        num_repeat = int(num_repeat_str) if num_repeat_str else 0
        # 예: [3] -> 3/9, [14] -> 14/99
        den_repeat_base = (10 ** len(self.__repeat) - 1) if self.__repeat else 1

        # 반복부는 비반복부의 자릿수만큼 10의 거듭제곱으로 나눠줘야 함
        # 예: 0.1[6] -> 1/10 + 6/90
        den_repeat = den_repeat_base * den_non_repeat

        # 3. 정수부와 소수부를 합쳐 전체 분수를 만듦
        # (정수부) + (비반복부 분수) + (반복부 분수)
        frac_num = num_non_repeat * den_repeat_base + num_repeat

        total_num = self.__int_part * den_repeat + frac_num
        total_den = den_repeat

        # 4. 부호 적용 및 약분
        total_num *= self.__sign
        common = math.gcd(total_num, total_den)
        return total_num // common, total_den // common

    @classmethod
    def from_fraction(cls, num, den):
        """Converts a (numerator, denominator) pair to a RepeatingDecimal object."""
        if den == 0:
            raise ZeroDivisionError("Denominator cannot be zero")
        if num == 0:
            return cls(0, 0, [], [])

        sign = 1 if num * den > 0 else -1
        num, den = abs(num), abs(den)

        int_part = num // den
        rem = num % den

        if rem == 0:
            return cls(sign, int_part, [], [])

        # 긴 나눗셈(long division)을 시뮬레이션하여 반복부를 찾음
        frac_digits = []
        remainders = {}  # {나머지: 위치} 저장

        while rem != 0 and rem not in remainders:
            remainders[rem] = len(frac_digits)
            rem *= 10
            frac_digits.append(rem // den)
            rem %= den

        if rem == 0:  # 나누어 떨어지는 경우 (반복부 없음)
            non_repeat_part = frac_digits
            repeat_part = []
        else:  # 반복되는 나머지가 나타난 경우
            start_pos = remainders[rem]
            non_repeat_part = frac_digits[:start_pos]
            repeat_part = frac_digits[start_pos:]

        return cls(sign, int_part, non_repeat_part, repeat_part)

    def __mul__(self, other):
        num1, den1 = self.to_fraction()
        num2, den2 = other.to_fraction()

        res_num = num1 * num2
        res_den = den1 * den2

        return RepeatingDecimal.from_fraction(res_num, res_den)

    def __truediv__(self, other):
        num1, den1 = self.to_fraction()
        num2, den2 = other.to_fraction()

        if num2 == 0:
            raise ZeroDivisionError("Division by zero")

        res_num = num1 * den2
        res_den = den1 * num2

        return RepeatingDecimal.from_fraction(res_num, res_den)

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
