from HW1_RepeatingDecimal import RepeatingDecimal, student_id

ps = [45238972, 78312467, 15927486, 67219356, 81437961, 50612793, 79341829, 23791841, 69517283, 42831769, 73916285, 98371249, 35497183, 61527389, 18294763, 56419837, 72149387, 84173925, 69428371, 15879243, 87216439, 36729185, 59182743, 72948163, 13674928, 64928371, 85713926, 49381725, 78624931, 25839147, 61289734, 74126389, 36581947, 51927364, 79361824, 15492736, 68943127, 82173654, 42985713, 57381926, 39172485, 72649381, 83571924, 19483726, 65829174, 71368259, 52491873, 38719625, 64928375, 81293746, 59371826, 27163849, 48729136, 63917284, 78519362, 12983764, 47193825, 65287149, 38745192, 93628174, 58371926, 72163849, 48931725, 67129384, 75291863, 19384725, 69812734, 51729386, 43981725, 67291834, 81273945, 39481726, 75629138, 12893764, 61372984, 72918364, 15827394, 59713824, 38471926, 72193846, 46291738, 59387124, 81927364, 74561938, 67123849, 52731849, 38917265, 69381725, 47291836, 85371926, 61928374, 75461928, 19283746, 53829174, 61293748, 72948136, 38472619, 57192834, 69827314, 24791836, 57]
ds = 84927481

class AnswerSuite:
    def __init__(self, sid):
        self.__student_id = sid
        self.__cs = int(sid) % ds
        self.__ls = int(sid[4:7])
        self.__gi = 0

    def next_random(self):
        self.__cs = (self.__cs + ps[self.__gi]) % (ds + self.__ls + ps[(self.__gi + 1) % len(ps)] % ds)
        self.__gi = (self.__gi + 1) % len(ps)
        return self.__cs

    def generate_dirty_random_repeating_decimal(self):
        sign = 1 if self.next_random() % 2 == 0 else -1
        int_part = self.next_random() % 200 - 100
        non_repeat_length = self.next_random() % 7
        repeat_length = self.next_random() % 7

        non_repeat = [self.next_random() % 40 - 20 for _ in range(non_repeat_length)]
        repeat = [self.next_random() % 40 - 20 for _ in range(repeat_length)]

        try:
            print(f"Generated repeating decimal: {sign}, {int_part}, {non_repeat}, {repeat}")
            print(RepeatingDecimal(sign, int_part, non_repeat, repeat))
            return RepeatingDecimal(sign, int_part, non_repeat, repeat)
        except Exception as e:
            print(e)
            raise e

    def generate_random_repeating_decimal(self):
        sign = 1 if self.next_random() % 2 == 0 else -1
        int_part = self.next_random() % 100
        non_repeat_length = self.next_random() % 7
        repeat_length = self.next_random() % 7

        non_repeat = [self.next_random() % 10 for _ in range(non_repeat_length)]
        repeat = [self.next_random() % 10 for _ in range(repeat_length)]

        try:
            return RepeatingDecimal(sign, int_part, non_repeat, repeat)
        except Exception as e:
            print(e)
            raise e
        
    def evaluate_random_equation(self):
        equation_length = self.next_random() % 10 + 1
        operations = [self.next_random() % 2 for _ in range(equation_length)]
        unary_operations = [self.next_random() % 5 for _ in range(equation_length)]

        result = self.generate_random_repeating_decimal()
        for i in range(equation_length):
            next_decimal = self.generate_random_repeating_decimal()
            if unary_operations[i] != 0:
                next_decimal = -next_decimal
            if operations[i] == 0:
                result = result + next_decimal
            else:
                result = result - next_decimal
        return result


    def test1(self):
        total = 0
        for i in range(10):
            dec = self.generate_dirty_random_repeating_decimal()
            sign = dec._RepeatingDecimal__sign
            int_part = dec._RepeatingDecimal__int_part
            non_repeat_part_length = len(dec._RepeatingDecimal__non_repeat)
            non_repeat_part = int(''.join(map(str, dec._RepeatingDecimal__non_repeat)) or "0")
            repeat_part_length = len(dec._RepeatingDecimal__repeat)
            repeat_part = int(''.join(map(str, dec._RepeatingDecimal__repeat)) or "0")
            total = (total + sign + int_part + non_repeat_part_length + non_repeat_part + repeat_part_length + repeat_part)  % 10000000
        print(f"Answer for 1: {total}")
            
    def test2(self):
        total = 0
        for i in range(100000):
            dec = self.evaluate_random_equation()
            repeated_part = ''.join(map(str, dec._RepeatingDecimal__repeat)) or "0"
            sign = dec._RepeatingDecimal__sign
            int_part = dec._RepeatingDecimal__int_part
            non_repeat_part_length = len(dec._RepeatingDecimal__non_repeat)
            non_repeat_part = int(''.join(map(str, dec._RepeatingDecimal__non_repeat)) or "0")
            repeat_part_length = len(dec._RepeatingDecimal__repeat)
            repeat_part = int(''.join(map(str, dec._RepeatingDecimal__repeat)) or "0")
            total = (total + sign + int_part + non_repeat_part_length + non_repeat_part + repeat_part_length + repeat_part)  % 10000000
        print(f"Answer for 2: {total}")


if __name__ == "__main__":
    suite = AnswerSuite(student_id)
    suite.test1()
    suite.test2()