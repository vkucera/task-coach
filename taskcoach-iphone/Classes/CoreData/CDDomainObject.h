//
//  CDDomainObject.h
//  
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>

@class CDFile;

@interface CDDomainObject :  NSManagedObject  
{
}

@property (nonatomic, retain) NSNumber * status;
@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSString * taskCoachId;
@property (nonatomic, retain) CDFile * file;

@end



