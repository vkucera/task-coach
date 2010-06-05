//
//  CDFile.h
//  
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>

@class CDDomainObject;

@interface CDFile :  NSManagedObject  
{
}

@property (nonatomic, retain) NSNumber * endHour;
@property (nonatomic, retain) NSNumber * startHour;
@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSString * guid;
@property (nonatomic, retain) NSSet* objects;

@end


@interface CDFile (CoreDataGeneratedAccessors)
- (void)addObjectsObject:(CDDomainObject *)value;
- (void)removeObjectsObject:(CDDomainObject *)value;
- (void)addObjects:(NSSet *)value;
- (void)removeObjects:(NSSet *)value;

@end

