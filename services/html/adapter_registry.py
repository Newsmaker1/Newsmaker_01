from services.html.adapters.default_adapter import (
    DefaultHTMLAdapter,
)

from services.html.adapters.egov_board_adapter import (
    EGovBoardAdapter,
)

class AdapterRegistry:

    _adapters = {

        # ==========================================
        # DEFAULT
        # ==========================================

        "egov_board": (
            EGovBoardAdapter
        ),
        
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
    # GET FALLBACKS
    # ==================================================

    @classmethod
    def get_fallback_adapters(
        cls,
        strategy: str | None,
    ) -> list:

        fallback_order = [

            "default",

        ]

        adapters = []

        used = set()

        # ==============================================
        # PRIMARY
        # ==============================================

        if (
            strategy
            and strategy
            in cls._adapters
        ):

            adapters.append(
                cls.get_adapter(
                    strategy
                )
            )

            used.add(strategy)

        # ==============================================
        # FALLBACKS
        # ==============================================

        for name in fallback_order:

            if name in used:
                continue

            adapters.append(
                cls.get_adapter(name)
            )

        return adapters

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
