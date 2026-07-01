"""
Judge0 Service — handles code execution for 20+ languages.
Sends code to Judge0, polls for result, returns stdout/stderr/verdict.
"""

import asyncio
import httpx
from typing import Optional
from app.config import settings
from app.schemas.schemas import ExecutionResult


# Judge0 language IDs
LANGUAGE_IDS = {
    "python":     71,   # Python 3.8
    "javascript": 63,   # Node.js 12
    "java":       62,   # Java 13
    "cpp":        54,   # C++ 17
    "c":          50,   # C (GCC 9.2)
    "typescript": 74,   # TypeScript 3.7
    "go":         60,   # Go 1.13
    "rust":       73,   # Rust 1.40
    "ruby":       72,   # Ruby 2.7
    "php":        68,   # PHP 7.4
    "swift":      83,   # Swift 5.2
    "kotlin":     78,   # Kotlin 1.3
}

STATUS_MAP = {
    1:  "queued",
    2:  "processing",
    3:  "accepted",
    4:  "wrong_answer",
    5:  "time_limit",
    6:  "compilation_error",
    7:  "runtime_error_sigsegv",
    8:  "runtime_error_sigfpe",
    9:  "runtime_error_sigabrt",
    10: "runtime_error_nzec",
    11: "runtime_error_other",
    12: "runtime_error_internal",
    13: "exec_format_error",
}


class Judge0Service:
    def __init__(self):
        self.base_url = settings.judge0_url
        self.timeout = httpx.Timeout(30.0)

    def _get_language_id(self, language: str) -> Optional[int]:
        return LANGUAGE_IDS.get(language.lower())

    async def execute(
        self,
        code: str,
        language: str,
        stdin: str = "",
        expected_output: Optional[str] = None,
    ) -> ExecutionResult:
        language_id = self._get_language_id(language)
        if not language_id:
            return ExecutionResult(
                status="unsupported_language",
                stderr=f"Language '{language}' is not supported for execution.",
                passed=False,
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Submit to Judge0
                submit_payload = {
                    "source_code": code,
                    "language_id": language_id,
                    "stdin": stdin,
                    "expected_output": expected_output,
                }

                submit_resp = await client.post(
                    f"{self.base_url}/submissions?base64_encoded=false&wait=false",
                    json=submit_payload,
                )
                submit_resp.raise_for_status()
                token = submit_resp.json().get("token")

                if not token:
                    return ExecutionResult(status="submission_failed", passed=False)

                # Poll for result (max 10 seconds)
                for _ in range(20):
                    await asyncio.sleep(0.5)
                    result_resp = await client.get(
                        f"{self.base_url}/submissions/{token}?base64_encoded=false"
                    )
                    result_resp.raise_for_status()
                    result = result_resp.json()

                    status_id = result.get("status", {}).get("id", 1)
                    if status_id > 2:  # Done processing
                        break

                status_name = STATUS_MAP.get(status_id, "unknown")
                stdout = result.get("stdout") or ""
                stderr = result.get("stderr") or ""
                compile_output = result.get("compile_output") or ""

                passed = (
                    status_id == 3
                    and (
                        expected_output is None
                        or stdout.strip() == expected_output.strip()
                    )
                )

                return ExecutionResult(
                    stdout=stdout,
                    stderr=stderr or compile_output,
                    compile_output=compile_output,
                    status=status_name,
                    time=result.get("time"),
                    memory=result.get("memory"),
                    passed=passed,
                )

        except httpx.ConnectError:
            # Judge0 not running — return a graceful fallback
            return ExecutionResult(
                status="judge_unavailable",
                stderr="Code execution service is not available. AI analysis still works.",
                passed=False,
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                stderr=str(e),
                passed=False,
            )

    async def run_test_cases(
        self,
        code: str,
        language: str,
        test_cases: list,
    ) -> dict:
        """Run code against multiple test cases and return pass/fail for each."""
        results = []
        passed_count = 0

        for i, tc in enumerate(test_cases):
            result = await self.execute(
                code=code,
                language=language,
                stdin=tc.get("input", ""),
                expected_output=tc.get("expected", ""),
            )
            results.append({
                "test_case": i + 1,
                "passed": result.passed,
                "status": result.status,
                "stdout": result.stdout,
                "expected": tc.get("expected", ""),
            })
            if result.passed:
                passed_count += 1

        return {
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "results": results,
        }


judge0_service = Judge0Service()
