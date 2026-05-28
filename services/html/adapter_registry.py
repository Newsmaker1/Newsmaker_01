from services.html.adapters.default_adapter import (
    DefaultHTMLAdapter,
)


class AdapterRegistry:

    _adapters = {

        # ==========================================
        # DEFAULT
        # ==========================================

        "default": (
            DefaultHTMLAdapter
        ),

    }

    # ==================================================
    # GET ADAPTER
    # ==================================================

    @classmethod
    def get_adapter(
        cls,
        strategy: str | None,
    ):

        if not strategy:

            strategy = "default"

        adapter_class = (
            cls._adapters.get(
                strategy,
                DefaultHTMLAdapter,
            )
        )

        return adapter_class()

    # ==================================================
    # REGISTER
    # ==================================================

    @classmethod
    def register(
        cls,
        name: str,
        adapter,
    ) -> None:

        cls._adapters[name] = adapter
