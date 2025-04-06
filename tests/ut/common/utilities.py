import queue


def assert_equal_objects(self, actual_param, expected_param):
    q = queue.Queue()
    q.put((actual_param, expected_param))
    while not q.empty():
        actual_param, expected_param = q.get()
        if isinstance(actual_param, (int, float, bool, str, type(None))):
            self.assertEqual(actual_param, expected_param)
        elif isinstance(actual_param, list):
            self.assertIsInstance(expected_param, list)
            self.assertEqual(len(actual_param), len(expected_param))
            for index, actual_param_list_item in enumerate(actual_param):
                q.put((actual_param_list_item, expected_param[index]))
        else:
            for k in actual_param.__dict__.keys():
                self.assertIn(k, expected_param.__dict__)
                if not k.startswith('__'):
                    q.put((getattr(actual_param, k), getattr(expected_param, k)))