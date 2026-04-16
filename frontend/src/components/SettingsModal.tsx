import React, { useState, useEffect } from 'react'
import { X, Save, Loader2 } from 'lucide-react'
import { api, LLMSettings } from '../services/api'

interface Props {
    isOpen: boolean
    onClose: () => void
}

const PROVIDERS = [
    { id: 'OpenAI', url: 'https://api.openai.com/v1', defaultModel: 'gpt-4o-mini' },
    { id: 'Anthropic Claude (需透過代理)', url: 'https://openrouter.ai/api/v1', defaultModel: 'anthropic/claude-3-5-sonnet' },
    { id: 'DeepSeek', url: 'https://api.deepseek.com', defaultModel: 'deepseek-chat' },
    { id: '硅基流動 (SiliconFlow)', url: 'https://api.siliconflow.cn/v1', defaultModel: 'Qwen/Qwen2.5-7B-Instruct' },
    { id: 'Minimax', url: 'https://api.minimax.chat/v1', defaultModel: 'abab6.5-chat' },
    { id: 'OpenRouter', url: 'https://openrouter.ai/api/v1', defaultModel: 'openai/gpt-4o-mini' },
    { id: 'Ollama', url: 'http://localhost:11434/v1', defaultModel: 'qwen2.5' },
    { id: '自訂端點', url: '', defaultModel: '' }
]

export function SettingsModal({ isOpen, onClose }: Props) {
    const [settings, setSettings] = useState<LLMSettings>({
        provider: 'OpenAI',
        base_url: 'https://api.openai.com/v1',
        api_key: '',
        model_name: 'gpt-4o-mini'
    })
    const [isLoading, setIsLoading] = useState(false)
    const [isSaving, setIsSaving] = useState(false)

    useEffect(() => {
        if (isOpen) {
            loadSettings()
        }
    }, [isOpen])

    const loadSettings = async () => {
        setIsLoading(true)
        try {
            const data = await api.settings.getLlm()
            setSettings(data)
        } catch (err) {
            console.error('Failed to load settings:', err)
        } finally {
            setIsLoading(false)
        }
    }

    const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const providerId = e.target.value
        const provider = PROVIDERS.find(p => p.id === providerId)
        if (provider) {
            setSettings(prev => ({
                ...prev,
                provider: provider.id,
                base_url: provider.url,
                model_name: provider.defaultModel
            }))
        } else {
            setSettings(prev => ({ ...prev, provider: providerId }))
        }
    }

    const handleSave = async () => {
        setIsSaving(true)
        try {
            await api.settings.updateLlm(settings)
            onClose()
        } catch (err) {
            console.error('Failed to save settings:', err)
            alert("儲存失敗: " + err)
        } finally {
            setIsSaving(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center">
            <div className="bg-slate-900 border border-slate-700/50 rounded-xl w-[500px] overflow-hidden shadow-2xl">
                <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-slate-800/50">
                    <h2 className="text-lg font-semibold text-white">模型供應商設定</h2>
                    <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded-md text-slate-400 hover:text-white transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                        </div>
                    ) : (
                        <>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">供應商 (Provider)</label>
                                <select
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={settings.provider}
                                    onChange={handleProviderChange}
                                >
                                    {PROVIDERS.map(p => (
                                        <option key={p.id} value={p.id}>{p.id}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Base URL</label>
                                <input
                                    type="text"
                                    value={settings.base_url}
                                    onChange={e => setSettings({ ...settings, base_url: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                                    placeholder="例如: https://api.openai.com/v1"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">API Key</label>
                                <input
                                    type="password"
                                    value={settings.api_key}
                                    onChange={e => setSettings({ ...settings, api_key: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                                    placeholder="請輸入 API Key (本機安全儲存)"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Model Name</label>
                                <input
                                    type="text"
                                    value={settings.model_name}
                                    onChange={e => setSettings({ ...settings, model_name: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                                    placeholder="例如: gpt-4o-mini 或 deepseek-chat"
                                />
                            </div>
                        </>
                    )}
                </div>

                <div className="p-4 border-t border-slate-700/50 bg-slate-800/50 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
                    >
                        取消
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || isLoading}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        儲存設定
                    </button>
                </div>
            </div>
        </div>
    )
}
