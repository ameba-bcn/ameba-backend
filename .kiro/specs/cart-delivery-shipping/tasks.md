# Implementation Plan: Cart Delivery & Shipping

## Overview

Additive implementation that extends the existing cart with a `shipping` JSONField, a delivery-fee `ItemVariant` flag, a `DeliveryFeeService` helper, updated serializers, and extended cart state flags. No existing API contracts are broken.

## Tasks

- [x] 1. Add `is_delivery_fee` flag to `ItemVariant` and create migration
  - Add `is_delivery_fee = models.BooleanField(default=False)` to `ItemVariant` in `api/models/item.py`
  - Generate migration `api/migrations/0081_itemvariant_is_delivery_fee.py` via `makemigrations`
  - _Requirements: 2.5, 6.2_

- [x] 2. Add `shipping` JSONField to `Cart` and create migration
  - Add `shipping = JSONField(blank=True, null=True)` to `Cart` in `api/models/cart.py`
  - Generate migration `api/migrations/0082_cart_shipping.py` via `makemigrations`
  - _Requirements: 1.1, 1.5_

- [x] 3. Create data migration for the DeliveryFee Item and ItemVariant
  - Write `api/migrations/0083_delivery_fee_item.py` as a data migration
  - Create one `Item` (name="Delivery Fee", description="Home delivery surcharge") and one `ItemVariant` (price=4.00, stock=-1, `is_delivery_fee=True`)
  - _Requirements: 2.1, 2.5_

- [x] 4. Implement `DeliveryFeeService` helper
  - [x] 4.1 Create `api/helpers/delivery_fee.py` with `ensure_delivery_fee(cart)` and `remove_delivery_fee(cart)`
    - `ensure_delivery_fee`: look up `ItemVariant` where `is_delivery_fee=True`; add a `CartItems` row only if not already present
    - `remove_delivery_fee`: delete any `CartItems` rows for that variant on the given cart
    - _Requirements: 2.1, 2.2_

  - [ ]* 4.2 Write unit tests for `DeliveryFeeService`
    - Test `ensure_delivery_fee` is idempotent (calling twice adds only one row)
    - Test `remove_delivery_fee` is a no-op when no fee row exists
    - _Requirements: 2.1, 2.2_

- [x] 5. Update discount logic in `Cart` to exempt the delivery fee
  - [x] 5.1 Modify `Cart.get_cart_items_with_discounts` in `api/models/cart.py`
    - When iterating, if `cart_item.item_variant.is_delivery_fee` is `True`, append `{..., 'discount': None}` and skip the discount lookup
    - _Requirements: 2.4, 2.5, 6.1_

  - [x] 5.2 Modify `Cart.discounts_by_value_desc` in `api/models/cart.py`
    - Return `[]` immediately when `item_variant.is_delivery_fee` is `True`
    - _Requirements: 6.2_

  - [ ]* 5.3 Write property test for delivery fee discount exemption
    - **Property 2: Delivery fee always excluded from discounts**
    - **Validates: Requirements 2.4, 2.5, 6.1, 6.2**

  - [ ]* 5.4 Write property test for cart amount with delivery fee
    - **Property 3: Cart amount includes delivery fee at full price**
    - **Validates: Requirements 2.3, 6.3**

- [x] 6. Extend `Cart.state` with shipping selection flags
  - In `Cart.state` property (`api/models/cart.py`), add:
    - `needs_shipping_selection = self.shipping is None`
    - `can_confirm_or_change_shipping = self.shipping is not None`
  - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 6.1 Write property test for cart state flags
    - **Property 6: Cart state flags are consistent with shipping field**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 7. Implement shipping serializers in `api/serializers/cart.py`
  - [x] 7.1 Add `DeliverySerializer`, `ShopPickupSerializer`, and `ShippingSerializer`
    - `DeliverySerializer`: fields `direccion`, `ciudad`, `telefono`, `dni` — all `CharField`, validate non-empty after strip
    - `ShopPickupSerializer`: field `shop` — `CharField`, validate non-empty after strip
    - `ShippingSerializer`: optional nested `delivery` and `shop_pickup`; `validate()` enforces exactly one non-null
    - _Requirements: 1.2, 1.3, 1.4, 3.2, 3.3, 3.4_

  - [ ]* 7.2 Write unit tests for `ShippingSerializer`
    - Valid delivery payload accepted
    - Valid shop_pickup payload accepted
    - Both keys non-null → rejected (HTTP 400)
    - Neither key present → rejected (HTTP 400)
    - Empty `direccion` → rejected (HTTP 400)
    - _Requirements: 3.2, 3.3, 3.4_

  - [ ]* 7.3 Write property test for shipping serializer round-trip
    - **Property 4: Shipping serializer round-trip**
    - **Validates: Requirements 1.2, 1.3, 1.4, 5.4, 5.5**

  - [ ]* 7.4 Write property test for invalid shipping rejection
    - **Property 5: Invalid shipping payloads are rejected**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 8. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Update `CartSerializer` to handle the `shipping` field
  - [x] 9.1 Add `shipping` as a writable field to `CartSerializer` in `api/serializers/cart.py`
    - Use `ShippingSerializer(required=False, allow_null=True)` as the field
    - Add `shipping` to `Meta.fields`; keep it writable (not in `read_only_fields`)
    - _Requirements: 5.1, 5.2_

  - [x] 9.2 Update `CartSerializer.update()` to persist shipping and manage the delivery fee
    - If `shipping` is in `validated_data`, set `instance.shipping = validated_data['shipping']`
    - If `delivery` key is non-null → call `ensure_delivery_fee(instance)`
    - Otherwise → call `remove_delivery_fee(instance)`
    - _Requirements: 3.1, 3.5, 3.6_

  - [ ]* 9.3 Write unit tests for `CartSerializer` shipping field
    - Serialized output includes `shipping: null` when unset
    - PATCH with valid delivery payload updates `cart.shipping` and adds fee item
    - PATCH with shop_pickup payload removes fee item
    - _Requirements: 5.1, 5.2_

  - [ ]* 9.4 Write property test for `CartSerializer` shipping field exposure
    - **Property 7: CartSerializer exposes shipping field correctly**
    - **Validates: Requirements 5.1, 5.3, 5.4, 5.5**

- [x] 10. Update `CartCheckoutSerializer` to include the `shipping` field
  - Add `shipping` to `CartCheckoutSerializer.Meta.fields`
  - _Requirements: 5.3_

  - [ ]* 10.1 Write unit test for `CartCheckoutSerializer` shipping field
    - Serialized output includes `shipping` field
    - _Requirements: 5.3_

- [x] 11. Wire up and integration test the full PATCH flow
  - [x] 11.1 Write integration tests in `api/tests/test_cart_shipping.py` extending `BaseTest`
    - `PATCH /api/carts/{id}/` with delivery payload → 200, `shipping` set, fee item present
    - `PATCH /api/carts/{id}/` switching to shop_pickup → fee item removed
    - `PATCH /api/carts/{id}/` with malformed payload → 400
    - Unauthenticated PATCH → 401
    - _Requirements: 3.1, 3.4, 3.5, 3.6_

  - [ ]* 11.2 Write property test for delivery fee presence iff delivery active
    - **Property 1: Delivery fee present if and only if delivery is active**
    - **Validates: Requirements 2.1, 2.2, 3.5, 3.6**

- [x] 12. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests use [Hypothesis](https://hypothesis.readthedocs.io/) — add to dev dependencies if not present
- Run tests with: `docker compose run --rm ameba-backend python manage.py test`
- Migrations 0081–0083 must be applied before running the app: `docker compose run --rm ameba-backend python manage.py migrate`
