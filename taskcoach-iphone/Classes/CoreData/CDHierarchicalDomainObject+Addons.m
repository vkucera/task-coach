//
//  CDHierarchicalDomainObject+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDHierarchicalDomainObject+Addons.h"

@implementation CDHierarchicalDomainObject (Addons)

- (NSSet *)selfAndChildren
{
	NSMutableSet *result = [[[NSMutableSet alloc] init] autorelease];
	[result addObject:self];

	for (CDHierarchicalDomainObject *child in self.children)
		[result unionSet:[child selfAndChildren]];

	return result;
}

@end
