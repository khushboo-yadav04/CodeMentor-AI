from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Problem
from app.schemas.schemas import ProblemCreate, ProblemResponse
from app.routers.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=List[ProblemResponse])
def list_problems(
    difficulty: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Problem)
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    return query.all()


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/seed", status_code=201)
def seed_problems(db: Session = Depends(get_db)):
    """Seed the database with starter problems. Run once on first launch."""
    if db.query(Problem).count() > 0:
        return {"message": "Problems already seeded"}

    problems = [
        {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Each input has exactly one solution, and you may not use the same element twice.",
            "difficulty": "easy",
            "tags": ["arrays", "hash map"],
            "concepts": ["arrays", "hash map"],
            "starter_code": {
                "python":     "def two_sum(nums, target):\n    # Your solution here\n    pass\n\n# Test\nprint(two_sum([2,7,11,15], 9))  # Expected: [0,1]",
                "javascript": "function twoSum(nums, target) {\n  // Your solution here\n}\n\nconsole.log(twoSum([2,7,11,15], 9));",
                "java":       "import java.util.*;\npublic class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Your solution here\n        return new int[]{};\n    }\n}",
                "cpp":        "#include <vector>\n#include <unordered_map>\nusing namespace std;\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Your solution here\n    }\n};",
            },
            "test_cases": [
                {"input": "2 7 11 15\n9", "expected": "[0, 1]"},
                {"input": "3 2 4\n6",    "expected": "[1, 2]"},
            ],
        },
        {
            "title": "Valid Parentheses",
            "description": "Given a string s containing only '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if open brackets are closed by the same type of brackets in the correct order.",
            "difficulty": "easy",
            "tags": ["strings", "stack"],
            "concepts": ["strings", "recursion"],
            "starter_code": {
                "python":     "def is_valid(s: str) -> bool:\n    # Hint: use a stack\n    pass\n\nprint(is_valid('()[]{}'))  # True\nprint(is_valid('(]'))       # False",
                "javascript": "function isValid(s) {\n  // Hint: use a stack\n}\nconsole.log(isValid('()[]{}'));",
                "java":       "public class Solution {\n    public boolean isValid(String s) {\n        // Hint: use a stack\n        return false;\n    }\n}",
                "cpp":        "#include <stack>\n#include <string>\nusing namespace std;\nclass Solution {\npublic:\n    bool isValid(string s) {\n        // Hint: use a stack\n        return false;\n    }\n};",
            },
            "test_cases": [
                {"input": "()[]{}", "expected": "True"},
                {"input": "(]",     "expected": "False"},
                {"input": "([)]",   "expected": "False"},
            ],
        },
        {
            "title": "Maximum Subarray",
            "description": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum. This is the classic Kadane's Algorithm problem.",
            "difficulty": "medium",
            "tags": ["arrays", "dynamic programming"],
            "concepts": ["arrays", "dynamic programming"],
            "starter_code": {
                "python":     "def max_subarray(nums):\n    # Hint: Kadane's algorithm\n    pass\n\nprint(max_subarray([-2,1,-3,4,-1,2,1,-5,4]))  # 6",
                "javascript": "function maxSubArray(nums) {\n  // Hint: Kadane's algorithm\n}\nconsole.log(maxSubArray([-2,1,-3,4,-1,2,1,-5,4]));",
                "java":       "public class Solution {\n    public int maxSubArray(int[] nums) {\n        // Hint: Kadane's algorithm\n        return 0;\n    }\n}",
                "cpp":        "class Solution {\npublic:\n    int maxSubArray(vector<int>& nums) {\n        // Hint: Kadane's algorithm\n        return 0;\n    }\n};",
            },
            "test_cases": [
                {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected": "6"},
                {"input": "1",                       "expected": "1"},
            ],
        },
        {
            "title": "Binary Search",
            "description": "Given an array of integers nums sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its index. Otherwise return -1. You must write an algorithm with O(log n) runtime complexity.",
            "difficulty": "easy",
            "tags": ["binary search", "arrays"],
            "concepts": ["binary search", "arrays"],
            "starter_code": {
                "python":     "def search(nums, target):\n    # Implement binary search — O(log n)\n    pass\n\nprint(search([-1,0,3,5,9,12], 9))  # 4",
                "javascript": "function search(nums, target) {\n  // O(log n) binary search\n}\nconsole.log(search([-1,0,3,5,9,12], 9));",
                "java":       "public class Solution {\n    public int search(int[] nums, int target) {\n        // O(log n)\n        return -1;\n    }\n}",
                "cpp":        "class Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        // O(log n)\n        return -1;\n    }\n};",
            },
            "test_cases": [
                {"input": "-1 0 3 5 9 12\n9", "expected": "4"},
                {"input": "-1 0 3 5 9 12\n2", "expected": "-1"},
            ],
        },
        {
            "title": "Climbing Stairs",
            "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
            "difficulty": "easy",
            "tags": ["dynamic programming", "recursion"],
            "concepts": ["dynamic programming", "recursion"],
            "starter_code": {
                "python":     "def climb_stairs(n: int) -> int:\n    # Think about it: how many ways to reach step n?\n    pass\n\nprint(climb_stairs(5))  # 8",
                "javascript": "function climbStairs(n) {\n  // Hint: think Fibonacci\n}\nconsole.log(climbStairs(5));",
                "java":       "public class Solution {\n    public int climbStairs(int n) {\n        return 0;\n    }\n}",
                "cpp":        "class Solution {\npublic:\n    int climbStairs(int n) {\n        return 0;\n    }\n};",
            },
            "test_cases": [
                {"input": "5", "expected": "8"},
                {"input": "3", "expected": "3"},
            ],
        },
    ]

    for p in problems:
        db.add(Problem(**p))
    db.commit()

    return {"message": f"Seeded {len(problems)} problems successfully"}
