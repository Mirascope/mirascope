from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "BadRequestError",
            "args": "('Error code: 400 - {\\'error\\': {\\'message\\': \"The response was filtered due to the prompt triggering Azure OpenAI\\'s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", \\'type\\': None, \\'param\\': \\'prompt\\', \\'code\\': \\'content_filter\\', \\'status\\': 400, \\'innererror\\': {\\'code\\': \\'ResponsibleAIPolicyViolation\\', \\'content_filter_result\\': {\\'hate\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'jailbreak\\': {\\'filtered\\': False, \\'detected\\': False}, \\'self_harm\\': {\\'filtered\\': True, \\'severity\\': \\'medium\\'}, \\'sexual\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'violence\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}}}}}',)",
            "original_exception": "Error code: 400 - {'error': {'message': \"The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", 'type': None, 'param': 'prompt', 'code': 'content_filter', 'status': 400, 'innererror': {'code': 'ResponsibleAIPolicyViolation', 'content_filter_result': {'hate': {'filtered': False, 'severity': 'safe'}, 'jailbreak': {'filtered': False, 'detected': False}, 'self_harm': {'filtered': True, 'severity': 'medium'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}}}",
            "provider": "azure",
            "status_code": "400",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "BadRequestError",
            "args": "('Error code: 400 - {\\'error\\': {\\'message\\': \"The response was filtered due to the prompt triggering Azure OpenAI\\'s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", \\'type\\': None, \\'param\\': \\'prompt\\', \\'code\\': \\'content_filter\\', \\'status\\': 400, \\'innererror\\': {\\'code\\': \\'ResponsibleAIPolicyViolation\\', \\'content_filter_result\\': {\\'hate\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'jailbreak\\': {\\'filtered\\': False, \\'detected\\': False}, \\'self_harm\\': {\\'filtered\\': True, \\'severity\\': \\'medium\\'}, \\'sexual\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'violence\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}}}}}',)",
            "original_exception": "Error code: 400 - {'error': {'message': \"The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", 'type': None, 'param': 'prompt', 'code': 'content_filter', 'status': 400, 'innererror': {'code': 'ResponsibleAIPolicyViolation', 'content_filter_result': {'hate': {'filtered': False, 'severity': 'safe'}, 'jailbreak': {'filtered': False, 'detected': False}, 'self_harm': {'filtered': True, 'severity': 'medium'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}}}",
            "provider": "azure",
            "status_code": "400",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "BadRequestError",
            "args": "('Error code: 400 - {\\'error\\': {\\'message\\': \"The response was filtered due to the prompt triggering Azure OpenAI\\'s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", \\'type\\': None, \\'param\\': \\'prompt\\', \\'code\\': \\'content_filter\\', \\'status\\': 400, \\'innererror\\': {\\'code\\': \\'ResponsibleAIPolicyViolation\\', \\'content_filter_result\\': {\\'hate\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'jailbreak\\': {\\'filtered\\': False, \\'detected\\': False}, \\'self_harm\\': {\\'filtered\\': True, \\'severity\\': \\'medium\\'}, \\'sexual\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'violence\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}}}}}',)",
            "original_exception": "Error code: 400 - {'error': {'message': \"The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", 'type': None, 'param': 'prompt', 'code': 'content_filter', 'status': 400, 'innererror': {'code': 'ResponsibleAIPolicyViolation', 'content_filter_result': {'hate': {'filtered': False, 'severity': 'safe'}, 'jailbreak': {'filtered': False, 'detected': False}, 'self_harm': {'filtered': True, 'severity': 'medium'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}}}",
            "provider": "azure",
            "status_code": "400",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "BadRequestError",
            "args": "('Error code: 400 - {\\'error\\': {\\'message\\': \"The response was filtered due to the prompt triggering Azure OpenAI\\'s content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", \\'type\\': None, \\'param\\': \\'prompt\\', \\'code\\': \\'content_filter\\', \\'status\\': 400, \\'innererror\\': {\\'code\\': \\'ResponsibleAIPolicyViolation\\', \\'content_filter_result\\': {\\'hate\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'jailbreak\\': {\\'filtered\\': False, \\'detected\\': False}, \\'self_harm\\': {\\'filtered\\': True, \\'severity\\': \\'medium\\'}, \\'sexual\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}, \\'violence\\': {\\'filtered\\': False, \\'severity\\': \\'safe\\'}}}}}',)",
            "original_exception": "Error code: 400 - {'error': {'message': \"The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766\", 'type': None, 'param': 'prompt', 'code': 'content_filter', 'status': 400, 'innererror': {'code': 'ResponsibleAIPolicyViolation', 'content_filter_result': {'hate': {'filtered': False, 'severity': 'safe'}, 'jailbreak': {'filtered': False, 'detected': False}, 'self_harm': {'filtered': True, 'severity': 'medium'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}}}",
            "provider": "azure",
            "status_code": "400",
        }
    }
)
