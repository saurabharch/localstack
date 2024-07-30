# LocalStack Resource Provider Scaffolding v2
from __future__ import annotations

from pathlib import Path
from typing import Optional, TypedDict

import localstack.services.cloudformation.provider_utils as util
from localstack.services.cloudformation.resource_provider import (
    OperationStatus,
    ProgressEvent,
    ResourceProvider,
    ResourceRequest,
)


class EC2SecurityGroupProperties(TypedDict):
    GroupDescription: Optional[str]
    GroupId: Optional[str]
    GroupName: Optional[str]
    Id: Optional[str]
    SecurityGroupEgress: Optional[list[Egress]]
    SecurityGroupIngress: Optional[list[Ingress]]
    Tags: Optional[list[Tag]]
    VpcId: Optional[str]


class Ingress(TypedDict):
    IpProtocol: Optional[str]
    CidrIp: Optional[str]
    CidrIpv6: Optional[str]
    Description: Optional[str]
    FromPort: Optional[int]
    SourcePrefixListId: Optional[str]
    SourceSecurityGroupId: Optional[str]
    SourceSecurityGroupName: Optional[str]
    SourceSecurityGroupOwnerId: Optional[str]
    ToPort: Optional[int]


class Egress(TypedDict):
    IpProtocol: Optional[str]
    CidrIp: Optional[str]
    CidrIpv6: Optional[str]
    Description: Optional[str]
    DestinationPrefixListId: Optional[str]
    DestinationSecurityGroupId: Optional[str]
    FromPort: Optional[int]
    ToPort: Optional[int]


class Tag(TypedDict):
    Key: Optional[str]
    Value: Optional[str]


REPEATED_INVOCATION = "repeated_invocation"


class EC2SecurityGroupProvider(ResourceProvider[EC2SecurityGroupProperties]):
    TYPE = "AWS::EC2::SecurityGroup"  # Autogenerated. Don't change
    SCHEMA = util.get_schema_path(Path(__file__))  # Autogenerated. Don't change

    def create(
        self,
        request: ResourceRequest[EC2SecurityGroupProperties],
    ) -> ProgressEvent[EC2SecurityGroupProperties]:
        """
        Create a new resource.

        Primary identifier fields:
          - /properties/Id

        Required properties:
          - GroupDescription

        Create-only properties:
          - /properties/GroupDescription
          - /properties/GroupName
          - /properties/VpcId

        Read-only properties:
          - /properties/Id
          - /properties/GroupId



        """
        model = request.desired_state
        ec2 = request.aws_client_factory.ec2

        params = {}

        if not model.get("GroupName"):
            params["GroupName"] = util.generate_default_name(
                request.stack_name, request.logical_resource_id
            )
        else:
            params["GroupName"] = model["GroupName"]

        if vpc_id := model.get("VpcId"):
            params["VpcId"] = vpc_id

        params["Description"] = model.get("GroupDescription", "")
        if model.get("Tags"):
            tags = [{"ResourceType": "security-group", "Tags": model.get("Tags")}]
            params["TagSpecifications"] = tags

        response = ec2.create_security_group(**params)
        model["GroupId"] = response["GroupId"]

        # When you pass the logical ID of this resource to the intrinsic Ref function,
        # Ref returns the ID of the security group if you specified the VpcId property.
        # Otherwise, it returns the name of the security group.
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-securitygroup.html#aws-resource-ec2-securitygroup-return-values-ref
        if "VpcId" in model:
            model["Id"] = response["GroupId"]
        else:
            model["Id"] = params["GroupName"]

        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=model,
            custom_context=request.custom_context,
        )

    def read(
        self,
        request: ResourceRequest[EC2SecurityGroupProperties],
    ) -> ProgressEvent[EC2SecurityGroupProperties]:
        """
        Fetch resource information


        """
        raise NotImplementedError

    def delete(
        self,
        request: ResourceRequest[EC2SecurityGroupProperties],
    ) -> ProgressEvent[EC2SecurityGroupProperties]:
        """
        Delete a resource


        """
        model = request.desired_state
        ec2 = request.aws_client_factory.ec2

        ec2.delete_security_group(GroupId=model["GroupId"])
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=model,
            custom_context=request.custom_context,
        )

    def update(
        self,
        request: ResourceRequest[EC2SecurityGroupProperties],
    ) -> ProgressEvent[EC2SecurityGroupProperties]:
        """
        Update a resource


        """
        raise NotImplementedError
