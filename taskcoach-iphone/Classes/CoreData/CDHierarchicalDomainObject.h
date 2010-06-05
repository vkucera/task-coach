//
//  CDHierarchicalDomainObject.h
//  
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDDomainObject.h"


@interface CDHierarchicalDomainObject :  CDDomainObject  
{
}

@property (nonatomic, retain) NSManagedObject * parent;
@property (nonatomic, retain) NSSet* children;

@end


@interface CDHierarchicalDomainObject (CoreDataGeneratedAccessors)
- (void)addChildrenObject:(NSManagedObject *)value;
- (void)removeChildrenObject:(NSManagedObject *)value;
- (void)addChildren:(NSSet *)value;
- (void)removeChildren:(NSSet *)value;

@end

