//
//  CDList.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "CDList.h"
#import "CDDomainObject.h"
#import "CDFile.h"


@implementation CDList
@dynamic name;
@dynamic objects;
@dynamic file;

- (void)addObjectsObject:(CDDomainObject *)value {    
    NSSet *changedObjects = [[NSSet alloc] initWithObjects:&value count:1];
    [self willChangeValueForKey:@"objects" withSetMutation:NSKeyValueUnionSetMutation usingObjects:changedObjects];
    [[self primitiveValueForKey:@"objects"] addObject:value];
    [self didChangeValueForKey:@"objects" withSetMutation:NSKeyValueUnionSetMutation usingObjects:changedObjects];
    [changedObjects release];
}

- (void)removeObjectsObject:(CDDomainObject *)value {
    NSSet *changedObjects = [[NSSet alloc] initWithObjects:&value count:1];
    [self willChangeValueForKey:@"objects" withSetMutation:NSKeyValueMinusSetMutation usingObjects:changedObjects];
    [[self primitiveValueForKey:@"objects"] removeObject:value];
    [self didChangeValueForKey:@"objects" withSetMutation:NSKeyValueMinusSetMutation usingObjects:changedObjects];
    [changedObjects release];
}

- (void)addObjects:(NSSet *)value {    
    [self willChangeValueForKey:@"objects" withSetMutation:NSKeyValueUnionSetMutation usingObjects:value];
    [[self primitiveValueForKey:@"objects"] unionSet:value];
    [self didChangeValueForKey:@"objects" withSetMutation:NSKeyValueUnionSetMutation usingObjects:value];
}

- (void)removeObjects:(NSSet *)value {
    [self willChangeValueForKey:@"objects" withSetMutation:NSKeyValueMinusSetMutation usingObjects:value];
    [[self primitiveValueForKey:@"objects"] minusSet:value];
    [self didChangeValueForKey:@"objects" withSetMutation:NSKeyValueMinusSetMutation usingObjects:value];
}



@end
