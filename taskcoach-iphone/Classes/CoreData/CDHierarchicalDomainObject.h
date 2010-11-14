//
//  CDHierarchicalDomainObject.h
//  
//
//  Created by Jérôme Laheurte on 14/11/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>
#import "CDDomainObject.h"


@interface CDHierarchicalDomainObject :  CDDomainObject  
{
}

@property (nonatomic, retain) NSDate * creationDate;
@property (nonatomic, retain) CDHierarchicalDomainObject * parent;
@property (nonatomic, retain) NSSet* children;

@end


@interface CDHierarchicalDomainObject (CoreDataGeneratedAccessors)
- (void)addChildrenObject:(CDHierarchicalDomainObject *)value;
- (void)removeChildrenObject:(CDHierarchicalDomainObject *)value;
- (void)addChildren:(NSSet *)value;
- (void)removeChildren:(NSSet *)value;

@end

