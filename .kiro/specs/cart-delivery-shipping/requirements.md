# Requirements Document

## Introduction

This feature adds shipping/delivery support to the Ameba cart. At checkout, users choose between home delivery or shop pickup. The choice is stored on the cart as a `shipping` field. If delivery is selected, a fixed €4 delivery fee is added to the cart as a special `CartItem` that is exempt from discount codes. The checkout flow checks whether a shipping preference already exists on the cart and either skips the selection step or presents a confirmation/edit page accordingly.

## Glossary

- **Cart**: The existing `Cart` model that holds a user's selected items before purchase.
- **CartItem**: A through-model entry linking an `ItemVariant` to a `Cart` (model: `CartItems`).
- **Delivery**: A home-delivery option containing address, city, phone, and DNI.
- **ShopPickup**: An in-store pickup option identifying the pickup shop.
- **Shipping**: A JSON structure on the `Cart` that holds either a `Delivery` or a `ShopPickup` (or both, with one active).
- **DeliveryFee**: A fixed €4 surcharge added as a `CartItem` when delivery is chosen. Exempt from all discount codes.
- **Checkout**: The existing multi-step purchase flow ending in payment.
- **ShippingAPI**: The API surface (endpoints + serializers) that manages the `shipping` field on a `Cart`.

---

## Requirements

### Requirement 1: Shipping Data Model

**User Story:** As a developer, I want a well-defined shipping data structure on the cart, so that delivery and pickup preferences are stored consistently.

#### Acceptance Criteria

1. THE `Cart` model SHALL include a nullable `shipping` JSONField that stores a `Shipping` object.
2. THE `Shipping` object SHALL contain a `delivery` key of type `Delivery` and/or a `shop_pickup` key of type `ShopPickup`, with at most one active at a time.
3. THE `Delivery` object SHALL contain the fields: `direccion` (string), `ciudad` (string), `telefono` (string), and `dni` (string).
4. THE `ShopPickup` object SHALL contain the field: `shop` (string).
5. WHEN the `shipping` field is null or absent, THE `Cart` SHALL be treated as having no shipping preference set.

---

### Requirement 2: Delivery Fee Cart Item

**User Story:** As a platform operator, I want a €4 delivery fee automatically added to the cart when delivery is chosen, so that the cost is reflected in the cart total.

#### Acceptance Criteria

1. WHEN a user selects home delivery, THE `Cart` SHALL include a `DeliveryFee` `CartItem` representing a fixed charge of 400 cents (€4.00).
2. WHEN a user switches from delivery to shop pickup, THE `Cart` SHALL remove the `DeliveryFee` `CartItem`.
3. THE `Cart.amount` property SHALL include the `DeliveryFee` amount in the total when delivery is active.
4. IF a `discount_code` is applied to the `Cart`, THEN THE `Cart` SHALL NOT apply any discount to the `DeliveryFee` `CartItem`.
5. THE `DeliveryFee` `CartItem` SHALL be identifiable by a stable flag or type so that discount logic can exclude it unconditionally.

---

### Requirement 3: Set or Update Shipping on Cart

**User Story:** As a user, I want to set or change my delivery/pickup preference on my cart, so that I can control how my order is fulfilled.

#### Acceptance Criteria

1. WHEN a `PATCH /api/carts/{id}/` request is received with a valid `shipping` payload, THE `ShippingAPI` SHALL update the `Cart.shipping` field and return the updated cart.
2. WHEN the `shipping` payload contains a `delivery` object, THE `ShippingAPI` SHALL validate that `direccion`, `ciudad`, `telefono`, and `dni` are all non-empty strings.
3. WHEN the `shipping` payload contains a `shop_pickup` object, THE `ShippingAPI` SHALL validate that `shop` is a non-empty string.
4. IF the `shipping` payload is malformed or missing required fields, THEN THE `ShippingAPI` SHALL return HTTP 400 with a descriptive validation error.
5. WHEN the `shipping` payload switches from delivery to shop pickup, THE `ShippingAPI` SHALL remove the `DeliveryFee` `CartItem` from the cart.
6. WHEN the `shipping` payload switches from shop pickup to delivery, THE `ShippingAPI` SHALL add the `DeliveryFee` `CartItem` to the cart.

---

### Requirement 4: Checkout Flow — Shipping Selection Gate

**User Story:** As a user, I want the checkout flow to ask me about delivery only when I haven't already chosen, so that I'm not asked redundant questions.

#### Acceptance Criteria

1. WHEN a user initiates checkout and `Cart.shipping` is null, THE `Cart` state SHALL expose a flag `needs_shipping_selection: true` so the frontend can redirect to the shipping selection page.
2. WHEN a user initiates checkout and `Cart.shipping` is already set, THE `Cart` state SHALL expose `needs_shipping_selection: false` and a flag `can_confirm_or_change_shipping: true` so the frontend can redirect to the confirmation/edit page.
3. THE `Cart.state` property SHALL include `needs_shipping_selection` and `can_confirm_or_change_shipping` boolean fields.
4. WHEN `Cart.shipping` is set and the user confirms without changes, THE `ShippingAPI` SHALL allow proceeding to payment without requiring a re-submission of shipping data.

---

### Requirement 5: Cart Serializer — Shipping Field Exposure

**User Story:** As a frontend developer, I want the cart API response to include the shipping field, so that the UI can display and edit the current shipping preference.

#### Acceptance Criteria

1. THE `CartSerializer` SHALL include the `shipping` field in its output, returning `null` when no shipping preference is set.
2. THE `CartSerializer` SHALL accept a `shipping` object in `PATCH` requests and delegate validation to the `ShippingSerializer`.
3. THE `CartCheckoutSerializer` SHALL include the `shipping` field so the checkout summary page can display the chosen delivery method.
4. WHEN the `shipping` field contains a `delivery` object, THE `CartSerializer` SHALL serialize all four delivery fields (`direccion`, `ciudad`, `telefono`, `dni`).
5. WHEN the `shipping` field contains a `shop_pickup` object, THE `CartSerializer` SHALL serialize the `shop` field.

---

### Requirement 6: Discount Exemption for Delivery Fee

**User Story:** As a platform operator, I want discount codes to never reduce the delivery fee, so that the €4 charge is always collected in full.

#### Acceptance Criteria

1. THE `Cart.get_cart_items_with_discounts` method SHALL return the `DeliveryFee` `CartItem` with `discount: None` unconditionally, regardless of any active `discount_code`.
2. WHEN `Cart.discounts_by_value_desc` is called for the `DeliveryFee` item variant, THE `Cart` SHALL return an empty list.
3. THE `Cart.amount` property SHALL compute the `DeliveryFee` at full price (400 cents) even when a discount code is active on the cart.
