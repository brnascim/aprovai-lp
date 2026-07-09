import Foundation

/// Minimal fixed-width big-integer helpers needed to emit an ADB/mincrypt
/// RSA public key: -n^-1 mod 2^32 and 2^k mod n. Words are little-endian
/// (index 0 = least significant 32 bits).
enum BigUInt32 {

    /// Computes -(n0^-1) mod 2^32 for an odd n0 (the mincrypt `n0inv` field),
    /// using Newton-Raphson iteration (doubles correct bits each round).
    static func negativeInverseMod2Pow32(_ n0: UInt32) -> UInt32 {
        precondition(n0 & 1 == 1, "modulus must be odd")
        var inv: UInt32 = n0 // correct mod 2^3 since n*n ≡ 1 (mod 8) for odd n
        for _ in 0..<5 {
            inv = inv &* (2 &- n0 &* inv)
        }
        return ~inv &+ 1 // = 0 - inv (mod 2^32)
    }

    /// Computes 2^exponentBits mod n via repeated modular doubling.
    /// `n` must be normalized (most significant word non-zero) and > 1.
    /// Returns a word array of the same length as `n`.
    static func powerOfTwoMod(_ n: [UInt32], exponentBits: Int) -> [UInt32] {
        precondition(!n.isEmpty && n.last != 0 && !(n.count == 1 && n[0] <= 1))
        // One extra word so the value can exceed n before each reduction.
        var r = [UInt32](repeating: 0, count: n.count + 1)
        r[0] = 1
        for _ in 0..<exponentBits {
            shiftLeftOne(&r)
            if compare(r, n) >= 0 {
                subtract(&r, n)
            }
        }
        return Array(r[0..<n.count])
    }

    static func shiftLeftOne(_ value: inout [UInt32]) {
        var carry: UInt32 = 0
        for i in 0..<value.count {
            let next = value[i] >> 31
            value[i] = (value[i] << 1) | carry
            carry = next
        }
        precondition(carry == 0, "overflow in shiftLeftOne")
    }

    /// Compares a and b as big integers; word arrays may differ in length.
    static func compare(_ a: [UInt32], _ b: [UInt32]) -> Int {
        let n = max(a.count, b.count)
        for i in stride(from: n - 1, through: 0, by: -1) {
            let av = i < a.count ? a[i] : 0
            let bv = i < b.count ? b[i] : 0
            if av != bv { return av > bv ? 1 : -1 }
        }
        return 0
    }

    /// a -= b (requires a >= b).
    static func subtract(_ a: inout [UInt32], _ b: [UInt32]) {
        var borrow: UInt64 = 0
        for i in 0..<a.count {
            let bv = UInt64(i < b.count ? b[i] : 0)
            let diff = UInt64(a[i]) &- bv &- borrow
            a[i] = UInt32(truncatingIfNeeded: diff)
            borrow = (diff >> 63) & 1 // top bit set means it wrapped
        }
        precondition(borrow == 0, "subtract underflow")
    }
}
