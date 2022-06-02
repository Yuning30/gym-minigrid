from dsl import *
from robot import *
import heapq
import argparse
import time
import multiprocess as mp

def _try_multiprocess(func, input_dict_list, num_cpu, max_process_time, max_timeouts):

    # Base case
    if max_timeouts == 0:
        return None

    pool = mp.Pool(processes=num_cpu, maxtasksperchild=1)
    parallel_runs = [pool.apply_async(func, kwds=input_dict) for input_dict in input_dict_list]
    try:
        results = [p.get(timeout=max_process_time) for p in parallel_runs]
    except Exception as e:
        print(str(e))
        print("Timeout Error raised... Trying again")
        pool.close()
        pool.terminate()
        pool.join()
        return _try_multiprocess(func, input_dict_list, num_cpu, max_process_time, max_timeouts-1)
    pool.close()
    pool.terminate()
    pool.join()
    return results

def execute_program_batch(task, seed, program):
    #input_dict_list = []
    results = []
    for s in seed:
        results.append(execute_program_single_seed(task ,s, program))
        #input_dict_list.append({"task": task, "seed": s, "program": copy.deepcopy(program)})
    # results = _try_multiprocess(execute_program_single_seed, input_dict_list, 12, 60000, 60000)
    # print(program)
    # print(results)
    total_reward = 0
    total_valid = 0
    for rwd in results:
        if rwd == 1:
            # reach bad states
            return 1
        else:
            total_reward += rwd
            total_valid += 1
    assert total_valid != 0
    # return average reward
    return (total_reward / total_valid)

def execute_program_single_seed(task, seed, program):
    env = MiniGridRobot(task, seed)
    try:
        program.exec(env)
    except NotImplementedError:
        pass
        # print("Something cannot being executed")
    except NegativeReward:
        print("Obtained negative reward, reach bad state")
        return 1
    except Done:
        if env.reward > 0:
            print("reward", env.reward)
            print("Found a solution")
            print(program)
            exit()
        else:
            print("Found a bad program")
            print(program)
            return 1
    if env.steps > env.max_steps:
        return 1
    assert env.reward == 0
    return -1 * env.reward # (reward is inverted to use in min heap)

def top_down_enumeration_with_pq(task, seed, initial_program):
    weight = 0.02
    pq = []
    reward = execute_program_batch(task, seed, initial_program)
    heapq.heappush(pq, (reward + weight * initial_program.rules, reward, initial_program))
    start = time.time()
    while len(pq) > 0:
        _, reward, p = heapq.heappop(pq)
        if reward != 0:
            print("reward is not 0")
        if reward == -1 and p.ground():
            print("Found a solution")
            print(p)
            print(f"rules: {p.rules}")
            # env = KarelRobot(task, seed)
            # p.exec(env)
            # env.draw()
            # print("Steps:", env.steps)
            exit()
        if reward == 1:
            continue
        end = time.time()
        if end - start > 5400:
            print(end - start)
            exit()
        new_programs = p.expand()
        for prog in new_programs:
            reward = execute_program_batch(task, seed, prog)
            # print(prog, reward)
            heapq.heappush(pq, (reward + weight * prog.rules, reward, prog))
        # if p.ground():
        #     print(p)
        #     print("before")
        #     env.draw()
        #     p.exec(env)
        #     print("after")
        #     env.draw()
        #     print(env.reward)
        #     if env.reward == 1:
        #         print("ground truth")
        #         exit()
        # programs = programs[1:] + p.expand()
    
def top_down_enumeration_with_pq_and_timer(task, seed, initial_program, timeout):
    start = time.time()
    weight = 0.02
    pq = []
    reward = execute_program_batch(task, seed, initial_program)
    heapq.heappush(pq, (reward + weight * initial_program.rules, reward, initial_program))
    best_prog = initial_program
    best_rwd = reward
    while len(pq) > 0:
        _, reward, p = heapq.heappop(pq)
        if reward < best_rwd and p.ground():
            best_rwd = reward
            best_prog = p
        if reward != 0:
            print("reward is not 0")
        if reward == -1 and p.ground():
            print("Found a solution")
            print(p)
            print(f"rules: {p.rules}")
            # env = KarelRobot(task, seed)
            # p.exec(env)
            # env.draw()
            # print("Steps:", env.steps)
            exit()
        if reward == 1:
            continue
        new_programs = p.expand()
        for prog in new_programs:
            reward = execute_program_batch(task, seed, prog)
            heapq.heappush(pq, (reward + weight * prog.rules, reward, prog))
        
        # check for time out
        end = time.time()
        if end - start > timeout:
            print("Timeout")
            print(best_prog)
            print(best_rwd)
            exit()


def top_down_enumeration(task, seed, initial_program):
    programs = [initial_program]
    while len(programs) > 0:
        p = programs[0]
        # print(p)
        # print(f"rules: {p.rules}")

        # execute p in env
        env = KarelRobot(task, seed)
        print("before")
        env.draw()
        try:
            p.exec(env)
            print("after")
            env.draw()
            if env.reward == 1:
                print("Found a solution")
                print(p)
                exit()
        except NotImplementedError:
            print("Something cannot being executed")
        # if p.ground():
        #     print(p)
        #     print("before")
        #     env.draw()
        #     p.exec(env)
        #     print("after")
        #     env.draw()
        #     print(env.reward)
        #     if env.reward == 1:
        #         print("ground truth")
        #         exit()
        programs = programs[1:] + p.expand()

if __name__ == "__main__":
    # task = "fourCorners"

    candidate = Prog()

    parser = argparse.ArgumentParser()
    parser.add_argument('--pq', type=bool, default=True)
    parser.add_argument('--task', type=str)
    args = parser.parse_args()
    task = args.task
    seed = [3]
    env = MiniGridRobot(task , 3)
    # env.env.render()
    if args.pq:
        print("with pq")
        top_down_enumeration_with_pq(task, seed, candidate)
        # top_down_enumeration_with_pq_and_timer(task, seed, candidate, 7200)
    else:
        print("without pq")
        top_down_enumeration(task, seed, candidate)