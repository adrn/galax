"""Test :mod:`galax.potential._potential.param.core`."""

from dataclasses import replace
from typing import Any, Generic, TypeVar

import astropy.units as u
import pytest
from jax.numpy import array_equal

import quaxed.array_api as xp

from galax.potential import AbstractParameter, ConstantParameter, UserParameter
from galax.potential._potential.param.core import ParameterCallable
from galax.typing import Unit

T = TypeVar("T", bound=AbstractParameter)


class TestAbstractParameter(Generic[T]):
    """Test the `galax.potential.AbstractParameter` class."""

    @pytest.fixture(scope="class")
    def param_cls(self) -> type[T]:
        return AbstractParameter

    @pytest.fixture(scope="class")
    def field_unit(self) -> Unit:
        return u.km

    @pytest.fixture(scope="class")
    def param(self, param_cls: type[T], field_unit: Unit) -> T:
        class TestParameter(param_cls):
            unit: Unit

            def __call__(self, t: Any, **kwargs: Any) -> Any:
                return t

        return TestParameter(unit=field_unit)

    # ===============================================================

    def test_init(self) -> None:
        """Test init `galax.potential.AbstractParameter` method."""
        # Test that the abstract class cannot be instantiated
        with pytest.raises(TypeError):
            AbstractParameter()

    def test_call(self) -> None:
        """Test `galax.potential.AbstractParameter` call method."""
        # Test that the abstract class cannot be instantiated
        with pytest.raises(TypeError):
            AbstractParameter()()

    def test_unit_field(self, param: T, field_unit: Unit) -> None:
        """Test `galax.potential.AbstractParameter` unit field."""
        assert param.unit == field_unit


##############################################################################


class TestConstantParameter(TestAbstractParameter[ConstantParameter]):
    """Test the `galax.potential.ConstantParameter` class."""

    @pytest.fixture(scope="class")
    def param_cls(self) -> type[T]:
        return ConstantParameter

    @pytest.fixture(scope="class")
    def field_value(self) -> float:
        return 1.0

    @pytest.fixture(scope="class")
    def param(self, param_cls: type[T], field_unit: Unit, field_value: float) -> T:
        return param_cls(field_value, unit=field_unit)

    # ===============================================================

    def test_call(self, param: T, field_value: float) -> None:
        """Test `galax.potential.ConstantParameter` call method."""
        assert param(t=1.0) == field_value
        assert param(t=1.0 * u.s) == field_value
        assert array_equal(param(t=xp.asarray([1.0, 2.0])), [field_value, field_value])

    def test_mul(self, param: T, field_value: float) -> None:
        """Test `galax.potential.ConstantParameter` multiplication."""
        expected = replace(param, value=field_value * 2)
        assert param * 2 == expected
        assert 2 * param == expected


##############################################################################


class TestParameterCallable:
    """Test the `galax.potential.ParameterCallable` class."""

    def test_issubclass(self) -> None:
        assert issubclass(AbstractParameter, ParameterCallable)
        assert issubclass(ConstantParameter, ParameterCallable)
        assert issubclass(UserParameter, AbstractParameter)

    def test_issubclass_false(self) -> None:
        assert not issubclass(object, ParameterCallable)

    def test_isinstance(self) -> None:
        assert isinstance(ConstantParameter(1.0, unit=u.km), ParameterCallable)
        assert isinstance(UserParameter(lambda t: t, unit=u.km), ParameterCallable)


class TestUserParameter(TestAbstractParameter[UserParameter]):
    """Test the `galax.potential.UserParameter` class."""

    @pytest.fixture(scope="class")
    def param_cls(self) -> type[T]:
        return UserParameter

    @pytest.fixture(scope="class")
    def field_func(self) -> ParameterCallable:
        def func(t: Any, **kwargs: Any) -> Any:
            return t

        return func

    @pytest.fixture(scope="class")
    def param(
        self, param_cls: type[T], field_unit: Unit, field_func: ParameterCallable
    ) -> T:
        return param_cls(field_func, unit=field_unit)

    # ===============================================================

    def test_call(self, param: T) -> None:
        """Test :class:`galax.potential.UserParameter` call method."""
        assert param(t=1.0) == 1.0
        assert param(t=1.0 * u.s) == 1.0 * u.s

        t = xp.asarray([1.0, 2.0])
        assert array_equal(param(t=t), t)
